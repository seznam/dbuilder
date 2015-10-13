{% block from -%}
FROM {{ name }}:{{ tag }}
{% endblock %}

RUN apt-get update
RUN apt-get install -y equivs devscripts --no-install-recommends --no-install-suggests

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
