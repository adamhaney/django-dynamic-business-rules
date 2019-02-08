=============================
Django Dynamic Business Rules
=============================

.. image:: https://badge.fury.io/py/django-dynamic-business-rules.svg
    :target: https://badge.fury.io/py/django-dynamic-business-rules

.. image:: https://travis-ci.org/adamhaney/django-dynamic-business-rules.svg?branch=master
    :target: https://travis-ci.org/adamhaney/django-dynamic-business-rules

.. image:: https://codecov.io/gh/adamhaney/django-dynamic-business-rules/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/adamhaney/django-dynamic-business-rules

A Django centric event driven rules engine for extensible and configurable responses to changes to django models and triggers.

Documentation
-------------

The full documentation is at https://django-dynamic-business-rules.readthedocs.io.

Quickstart
----------

Install Django Dynamic Business Rules::

    pip install django-dynamic-business-rules

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dynamic_business_rules.apps.DynamicBusinessRulesConfig',
        ...
    )

Add Django Dynamic Business Rules's URL patterns:

.. code-block:: python

    from dynamic_business_rules import urls as dynamic_business_rules_urls


    urlpatterns = [
        ...
        url(r'^', include(dynamic_business_rules_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
