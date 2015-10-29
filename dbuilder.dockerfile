{% block from -%}
FROM {{ name }}:{{ tag }}
{% endblock %}

RUN apt-get update && \
echo 'APT::Install-Recommends "0";' > /etc/apt/apt.conf.d/10no-recommends && \
echo 'APT::Install-Suggests "0";' > /etc/apt/apt.conf.d/10no-suggests && \
apt-get install -y equivs devscripts

{%- block volumes %}
VOLUME /dbuilder/bin/
VOLUME /dbuilder/sources/
VOLUME /dbuilder/build/
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
