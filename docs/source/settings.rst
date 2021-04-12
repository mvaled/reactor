Settings
========

.. module:: django.settings

.. data:: REACTOR_AUTO_BROADCAST

   A boolean (default is False).  When enabled will activate listeners for
   every time a model is created, modified or deleted, and will broadcast a
   message related to that modification that you can subscribe to and use to
   refresh your components in real-time, you can fine tune what kind of
   notification you want to get by turning this in a dictionary, for example::

	 AUTO_BROADCAST = {
       # model_a
       # model_a.del
       # model_a.new
       'MODEL': True,

       # model_a.1234
       'MODEL_PK': True,

       # model_b.1234.model_a_set
       # model_b.1234.model_a_set.new
       # model_b.1234.model_a_set.del
       'RELATED': True,

       # model_b.1234.model_a_set
       # model_a.1234.model_b_set
       'M2M': True,
	 }


.. data:: REACTOR_USE_HTML_DIFF

   A boolean (default is True).  When enabled uses ``difflib`` to create diffs
   to patch the front-end, reducing bandwidth.

.. data:: REACTOR_USE_HMIN

   A boolean (default is False).  When enabled and ``django-hmin`` is
   installed will use it to minified the HTML of the components and save
   bandwidth.
