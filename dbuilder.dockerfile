{% block from -%}
FROM {{ name }}:{{ tag }}
{% endblock %}

RUN bash -c "mkdir -p /dbuilder/{additional_packages,bin,sources,build}/"

{%- block update_and_setup %}
{% endblock %}

{%- block volumes %}
VOLUME /dbuilder/bin/ /dbuilder/sources/ /dbuilder/build/
{% endblock %}

{%- block workdir %}
WORKDIR /dbuilder/build/
{% endblock -%}

{% macro run_script(name) -%}
ADD {{name}} /dbuilder/bin/{{name}}
ENTRYPOINT /dbuilder/bin/{{name}}
{% endmacro %}

{%- block custom %}
{% endblock -%}

{%- block labels %}
ARG build_date=""
ARG vcs_ref=""

LABEL org.label-schema.schema-version="1.0.0-rc.1" \
      org.label-schema.vendor="Seznam.cz, a.s." \
      org.label-schema.build-date="$build_date" \
      org.label-schema.vcs-url="https://github.com/seznam/dbuilder" \
      org.label-schema.vcs-ref="$vcs_ref" \
      org.label-schema.name="dbuilder" \
      org.label-schema.description="Docker images for building packages with clean dependencies in multiple distributions." \
      org.label-schema.usage="https://github.com/seznam/dbuilder" \
      org.label-schema.url="https://github.com/seznam/dbuilder" \
      org.label-schema.docker.cmd="docker run --rm -v `pwd`:/dbuilder/sources" \
      org.label-schema.docker.cmd.devel="docker run -v `pwd`:/dbuilder/sources"
{% endblock -%}
