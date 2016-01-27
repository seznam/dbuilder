{% block from -%}
FROM {{ name }}:{{ tag }}
{% endblock %}

RUN bash -c "mkdir -p /dbuilder/{additional_packages,bin,sources,build}/"

{%- block update_and_setup %}
{% endblock %}

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
