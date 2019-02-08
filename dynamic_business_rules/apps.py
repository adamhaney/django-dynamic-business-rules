from django.apps import AppConfig

from .models import BusinessRuleSet


class DynamicBusinessRulesConfig(AppConfig):
    name = 'dynamic_business_rules'

    def ready(self):
        for ruleset in BusinessRuleSet.objects.all:
            ruleset.signal_object.connect(ruleset.signal_callback)
