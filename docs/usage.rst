=====
Usage
=====

To use Django Dynamic Business Rules in a project, add it to your `INSTALLED_APPS`:

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
