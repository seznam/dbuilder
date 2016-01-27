{% extends "dbuilder.dockerfile" %}

{%- block update_and_setup %}
RUN apt-get update && \
echo 'APT::Install-Recommends "0";' > /etc/apt/apt.conf.d/10no-recommends && \
echo 'APT::Install-Suggests "0";' > /etc/apt/apt.conf.d/10no-suggests && \
apt-get install -y equivs devscripts dpkg-dev
{% endblock %}

{%- block custom %}
ENV DBUILDER_BUILD_CMD="dpkg-buildpackage -j${NCPUS}"

{%- if 'preinstall_packages' in jinja_env %}
RUN apt-get install -y {{ ' '.join(jinja_env['preinstall_packages']) }}
{%- endif %}

{{ run_script('run_dpkg.sh') }}
{%- endblock %}
