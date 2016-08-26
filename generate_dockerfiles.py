#!/usr/bin/env python3
import requests
import json
import os

def get_repository_tags(url):

    response = requests.get(url)
    response.raise_for_status()
    tags = json.loads(response.text)

    return list(tags.keys())

def str2bool(arg):
    return arg.lower() in ["true", "1", "yes"]

class Registry:
    url = None
    version = None
    verify_certs = True

    def __init__(self, registry_url, verify_certs=True):
        self.url = registry_url
        self.verify_certs = verify_certs

    def __repr__(self):
        return "<Registry ({}) {}>".format(self.version, self.url)

    def get_tags(self, repository):
        raise NotImplementedError()

    @classmethod
    def create(cls, registry_url, verify_certs=True):
        version_lookup = [
            {"class": Registry_v2, "url": "https://{}/v2/"},
            {"class": Registry_v1, "url": "https://{}/v1/_ping"},
        ]

        for version in version_lookup:
            url = version["url"].format(registry_url)
            response = requests.get(url, verify=verify_certs)
            if response.status_code == 200:
                return version["class"](registry_url, verify_certs)

        return NotImplemented("registry not recognized")


class Registry_v1(Registry):

    def __init__(self, registry_url, verify_certs):
        Registry.__init__(self, registry_url, verify_certs)
        self.version = "v1"

    def get_tags(self, repo):
        url = "https://{}/v1/repositories/{}/tags".format(self.url, repo)
        response = requests.get(url, verify=self.verify_certs)
        response.raise_for_status()
        tags = json.loads(response.text)

        return list(tags.keys())

class Registry_v2(Registry):

    def __init__(self, registry_url, verify_certs):
        Registry.__init__(self, registry_url, verify_certs)
        self.version = "v2"

    def get_tags(self, repo):
        url = "https://{}/v2/{}/tags/list".format(self.url, repo)
        response = requests.get(url, verify=self.verify_certs)
        response.raise_for_status()
        tags = json.loads(response.text)["tags"]
        return tags

class Repository:
    host = ''
    namespace = ''
    name = ''
    tag = ''

    def __init__(self, repository_identifier):
        domain_split_point = repository_identifier.find('.')
        host_split_point = repository_identifier.find('/')
        if domain_split_point != -1 and domain_split_point < host_split_point:
            self.host = repository_identifier[:host_split_point]
            rest = repository_identifier[host_split_point+1:]
        else:
            self.host = ''
            rest = repository_identifier

        name_split_point = rest.rfind('/')
        if name_split_point == -1:
            self.namespace = ''
        else:
            self.namespace = rest[:name_split_point]
            rest = rest[name_split_point+1:]

        tag_split_point = rest.find(':')
        if tag_split_point == -1:
            self.name = rest
            self.tag = ''
        else:
            self.name = rest[:tag_split_point]
            self.tag = rest[tag_split_point+1:]

        assert self.name != ''

    def get_repository_identifier(self):
        result = ''
        if self.host:
            result += self.host + '/'
        if self.namespace:
            result += self.namespace + '/'
        if self.name:
            result += self.name
        if self.tag:
            result += ':' + self.tag
        return result

    def get_image_full_name(self):
        if self.namespace:
            return self.namespace + '/' + self.name
        else:
            return self.name

    def get_host_prefix(self):
        if self.host:
            return self.host + '/'
        else:
            return ''

    def get_image_path(self):
        return self.get_host_prefix() + self.get_image_full_name()


def test_class_repository():
    repository_identifier = 'debian'
    repository = Repository(repository_identifier)
    assert repository.host == ''
    assert repository.namespace == ''
    assert repository.name == 'debian'
    assert repository.tag == ''
    assert repository.get_repository_identifier() == repository_identifier
    assert repository.get_image_full_name() == 'debian'
    assert repository.get_image_path() == 'debian'

    repository_identifier = 'debian:latest'
    repository = Repository(repository_identifier)
    assert repository.host == ''
    assert repository.namespace == ''
    assert repository.name == 'debian'
    assert repository.tag == 'latest'
    assert repository.get_repository_identifier() == repository_identifier
    assert repository.get_image_full_name() == 'debian'
    assert repository.get_image_path() == 'debian'

    repository_identifier = 'library/debian:latest'
    repository = Repository(repository_identifier)
    assert repository.host == ''
    assert repository.namespace == 'library'
    assert repository.name == 'debian'
    assert repository.tag == 'latest'
    assert repository.get_repository_identifier() == repository_identifier
    assert repository.get_image_full_name() == 'library/debian'
    assert repository.get_image_path() == 'library/debian'

    repository_identifier = 'docker.dev/szn-jessie:latest'
    repository = Repository(repository_identifier)
    assert repository.host == 'docker.dev'
    assert repository.namespace == ''
    assert repository.name == 'szn-jessie'
    assert repository.tag == 'latest'
    assert repository.get_repository_identifier() == repository_identifier
    assert repository.get_image_full_name() == 'szn-jessie'
    assert repository.get_image_path() == 'docker.dev/szn-jessie'

    repository_identifier = 'docker.dev/library/szn-jessie:latest'
    repository = Repository(repository_identifier)
    assert repository.host == 'docker.dev'
    assert repository.namespace == 'library'
    assert repository.name == 'szn-jessie'
    assert repository.tag == 'latest'
    assert repository.get_repository_identifier() == repository_identifier
    assert repository.get_image_full_name() == 'library/szn-jessie'
    assert repository.get_image_path() == 'docker.dev/library/szn-jessie'


def convert_docker_tag_to_makefile_target(docker_tag):
    return docker_tag.replace('/', '__').replace(':', '~')


def generate_dockerfiles(output_dir, configuration_files):
    import os
    import yaml
    import jinja2
    import copy

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    makefile = ("#!/usr/bin/make -f\n"
                "all: build\n\t\n"
                ".PHONY: build push all\n"
                "DOCKER_PUSH_CMD :=docker push\n"
                "DOCKER_BUILD_CMD :=docker build --pull --no-cache\n"
                "DOCKER_BUILD_CONTEXT :=../\n\n\n")

    processed_names = {}

    for configuration_file in configuration_files:
        with open(configuration_file, 'r') as configuration_f:
            config = yaml.load(configuration_f)

            dbuilder_namespace_mapping = config['dbuilder-namespace-mapping'] if 'dbuilder-namespace-mapping' in config else {}

            repo_group = []

            for repository_identifier, settings in config['packages'].items():
                repository = Repository(repository_identifier)
                if not repository.host:
                    repository.host = 'docker.io'

                if repository.host in dbuilder_namespace_mapping:
                    dbuilder_namespace = dbuilder_namespace_mapping[repository.host]
                else:
                    dbuilder_namespace = 'library'

                name = repository.name if repository.namespace == '' else repository.namespace + '__' + repository.name

                docker_tag_repo = repository.get_host_prefix() + dbuilder_namespace + '/dbuilder'
                repo_group.append(convert_docker_tag_to_makefile_target(docker_tag_repo))

                name_group = []

                for template_settings in settings['templates']:
                    template_file_abspath = os.path.abspath(os.path.join(os.path.dirname(configuration_file), template_settings['file']))
                    template_file_jinja_relpath = os.path.relpath(template_file_abspath, os.path.dirname(template_file_abspath))

                    tags = template_settings['tags']
                    if isinstance(tags, str):
                        if tags.lower() == 'all':
                            verify_certs = str2bool(os.getenv('VERIFY_CERTS', '1'))
                            registry = Registry.create(repository.host, verify_certs)
                            tags = registry.get_tags(repository.get_image_full_name())

                    suffix = '_' + template_settings['suffix'] if 'suffix' in template_settings else ''
                    jinja_env = template_settings['jinja_env'] if 'jinja_env' in template_settings else {}

                    docker_tag_name = docker_tag_repo + ':' + name + suffix
                    name_group.append(convert_docker_tag_to_makefile_target(docker_tag_name))

                    tag_group = []
                    for tag in tags:
                        template_loader = jinja2.FileSystemLoader(os.path.dirname(template_file_abspath))
                        template_environment = jinja2.Environment(loader=template_loader)
                        template = template_environment.get_template(template_file_jinja_relpath)

                        dockerfile_data = template.render(name=repository.get_image_path(), tag=tag, jinja_env=jinja_env)

                        docker_tag = docker_tag_name + '_' + str(tag)

                        makefile_target = convert_docker_tag_to_makefile_target(docker_tag)
                        tag_group.append(makefile_target)

                        dockerfile_filename = docker_tag.replace('/', '__') + '.dockerfile'

                        # Docker hub is special so you cannot use it's hostname
                        # as with other repositories or push will fail
                        docker_tag = docker_tag.replace('docker.io/', '')
                        # Docker at local machine differentiates between library/<name> and <name>
                        # so we will simplify it
                        docker_tag = docker_tag.replace('library/', '')

                        makefile += 'build-{}:\n\t$(DOCKER_BUILD_CMD) -f {} -t {} $(DOCKER_BUILD_CONTEXT)\n'.format(
                                    makefile_target, dockerfile_filename, docker_tag)
                        makefile += 'push-{}:\n\t$(DOCKER_PUSH_CMD) {}\n\n'.format(
                                    makefile_target, docker_tag)

                        if dockerfile_filename in processed_names:
                            raise RuntimeError(dockerfile_filename + " has already been processed")
                        else:
                            processed_names[dockerfile_filename] = None

                        with open(os.path.join(output_dir, dockerfile_filename), 'w+') as dockerfile_f:
                            dockerfile_f.write(dockerfile_data)

                    makefile_target_name = convert_docker_tag_to_makefile_target(docker_tag_name)
                    makefile += 'build-{}: {}\n\n'.format(makefile_target_name, ' '.join(
                                map(lambda x: 'build-' + x, tag_group)))
                    makefile += 'push-{}: {}\n\n'.format(makefile_target_name, ' '.join(
                                map(lambda x: 'push-' + x, tag_group)))
                    makefile += '.PHONY: build-{} push-{}\n\n'.format(makefile_target_name, makefile_target_name)

                makefile_target_repo = convert_docker_tag_to_makefile_target(docker_tag_repo)
                makefile += 'build-{}: {}\n\n'.format(makefile_target_repo, ' '.join(
                            map(lambda x: 'build-' + x, name_group)))
                makefile += 'push-{}: {}\n\n'.format(makefile_target_repo, ' '.join(
                            map(lambda x: 'push-' + x, name_group)))
                makefile += '.PHONY: build-{} push-{}\n\n'.format(makefile_target_repo, makefile_target_repo)

            makefile += 'build: {}\n\n'.format(' '.join(map(lambda x: 'build-' + x, repo_group)))
            makefile += 'push: {}\n\n'.format(' '.join(map(lambda x: 'push-' + x, repo_group)))

    with open(os.path.join(output_dir, 'Makefile'), 'w+') as makefile_f:
        makefile_f.write(makefile)


def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-c', '--configuration-file', dest='configuration_file', default='config.yaml',
                      help="Configuration file path [%default]")
    parser.add_option('-o', '--output-dir', dest='output_dir', default='./dockerfiles/',
                      help="Output directory [%default]")
    parser.set_defaults(verbose=True)
    (options, args) = parser.parse_args()

    generate_dockerfiles(options.output_dir, [options.configuration_file])


if __name__ == '__main__':
    test_class_repository()
    main()
