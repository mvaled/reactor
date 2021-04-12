===============
 Back-end APIs
===============

Template tags and filters of ``reactor`` library
================================================

- ``{% reactor_headers %}``: that includes the necessary JavaScript to make this
  library work. ~5Kb of minified JS, compressed with gz or brotli.

- ``{% component 'x-component-name' param1=1 param2=2 %}``: Renders a component
  by its name and passing whatever parameters you put there to the
  ``Component.mount`` method.

- ``tojson``: Takes something and renders it in JSON, the ``ReactorJSONEncoder``
  extends the ``DjangoJSONEncoder`` it serializes a ``Model`` instance to its ``id``
  and a ``QuerySet`` as a list of ``ids``.

- ``tojson_safe``: Same as ``tojson`` but does not "HTML escapes" the output.

- ``then``: Use as a shorthand for if, ``{% if expression %}print-this{% endif
  %}`` is equivalent to ``{{ expresssion|then:'print-this' }}``.

- ``ifnot``: Use a shorthand for if not, ``{% if not expression %}print-this{%
  endif %}`` is equivalent to ``{{ expresssion|ifnot:'print-this' }}, and can
  be concatenated with then, like in: ``{{
  expression|then:'positive'|ifnot:'negative' }}``

- ``eq``: Compares its arguments and returns ``"yes"`` or empty string, ``{{
  this_thing|eq:other_thing|then:'print-this' }}``.

- ``cond``: Allows simple conditional presence of a string: ``{% cond {'hidden':
  is_hidden } %}``.

- ``class``: Use it to handle conditional classes: ``<div {% class {'nav_bar':
  True, 'hidden': is_hidden} %}></div>``.

``reactor.component`` module
============================

- ``Component``: This is the base component you should extend.

- ``AuthComponent``: Extends ``Component`` and ensures the user is logged in.

- ``broadcast(*names)``: Broadcasts the given names too all the system.

- ``on_commit(function)(*args, **kwargs)``: Calls ``function`` with the given
  arguments after database commit.

Component API
=============

- ``__init__``: Is responsable for the component initialization, pass what
  ever you need to bootstrap the component state.

- ``template_name``: Set the name of the template of the component.

- ``extends``: Tag name HTML element the component extends.

- ``_subscribe(*names)``: Subscribes the current component to the given signal
  names, when one of those signals is broadcasted the component is refreshed,
  meaning that ``mount`` is called passing the result ``serialize`` and the
  component is re-rendered.

- ``visit(url, action='advance', **kwargs )``: Resolves the ``url`` using
  ``**kwargs``, and depending on ``action`` the navigation will be ``advance``
  (pushState) or ``replace`` (repalceState).

- ``destroy()``: Removes the component from the interface.

- ``_send(_name, id=None, **kwargs)``: Sends a message with the name ``_name``
  to the component with ``id``, if ``id`` is ``None`` the message is sent to
  the current component.

- ``_send_parent(_name, kwargs)``: Sends a message with the name ``_name`` to
  the parent component.
