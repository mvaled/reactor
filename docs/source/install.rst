Installation and setup
======================

.. code-block:: bash

   pip install django-reactor

Reactor makes use of Django Channels.  By default we use an InMemory channel
layer which is not capable of a real broadcasting, so you might wanna use the
`Redis one`__.

__ https://channels.readthedocs.io/en/latest/topics/channel_layers.html

Add both ``reactor`` and ``channels`` to your ``INSTALLED_APPS`` **before**
the other Django applications so channels can override the `runserver`
command.

.. code-block:: python

   INSTALLED_APPS = [
	   'reactor',
	   'channels',
	   ...
   ]

   # ...

   ASGI_APPLICATION = 'project_name.asgi.application'

and modify your ``project_name/asgi.py`` file like::

  import os
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

  import django
  django.setup()

  from channels.auth import AuthMiddlewareStack
  from channels.routing import ProtocolTypeRouter, URLRouter
  from django.core.asgi import get_asgi_application
  from reactor.urls import websocket_urlpatterns

  application = ProtocolTypeRouter({
      'http': get_asgi_application(),
      'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
  })

.. note:: Since version 2, django-reactor autoloads any ``live.py`` file in
          your applications with the hope to find there Reactor Components so
          they get registered and can be instantiated.
