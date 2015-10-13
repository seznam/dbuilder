{% extends "dbuilder.dockerfile" %}

{%- block custom %}
ENV DBUILDER_BUILD_CMD="dpkg-buildpackage -j${NCPUS}"

{%- if 'preinstall_packages' in jinja_env %}
RUN apt-get install -y {{ ' '.join(jinja_env['preinstall_packages']) }}
{%- endif %}

{{ run_script('run_dpkg.sh') }}
{%- endblock %}
