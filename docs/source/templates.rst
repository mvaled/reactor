=======================
 Interactive templates
=======================

In the templates where you want to use reactive components you have to load
the reactor static files. So do something like this so the right JavaScript
gets loaded:

.. code-block:: django

   {% load reactor %}
   <!doctype html>
   <html>
	 <head>
		....
		{% reactor_header %}
	 </head>
	 ...
   </html>

Don't worry if you put this as early as possible, the scripts are loaded using
``<script defer>`` so they will be downloaded in parallel with the html, and
then all is loaded they are executed.
