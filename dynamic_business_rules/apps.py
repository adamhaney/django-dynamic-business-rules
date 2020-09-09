from django.apps import AppConfig


class DynamicBusinessRulesConfig(AppConfig):
    name = 'dynamic_business_rules'

    def ready(self):
        from .models import BusinessRuleSet

        for ruleset in BusinessRuleSet.objects.all():
            ruleset.signal_object.connect(ruleset.signal_callback)
