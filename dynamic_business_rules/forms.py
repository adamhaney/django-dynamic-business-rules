import inspect

from django import forms
from django.conf import settings
from django.utils.module_loading import import_string

from .models import BusinessRuleSet, Condition, Action


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def modules_with_variables():
    return [
        app
        for app
        in map(lambda app: f"{app}.dynamic_rule_variables", settings.INSTALLED_APPS)
        if module_exists(app)
    ]


def modules_with_actions():
    return [
        app
        for app
        in map(lambda app: f"{app}.dynamic_rule_actions", settings.INSTALLED_APPS)
        if module_exists(app)
    ]


def classes_from_module_list(module_list):
    for module in module_list:
        for name, obj in inspect.getmembers(import_string(module)):
            if inspect.isclass(obj):
                class_name = obj.__name__
                yield f"{module}.{class_name}"


class BusinessRuleSetAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variables_class'] = forms.ChoiceField(
            choices=self.variables_class_choices,
            widget=forms.Select(attrs={'style': 'font-size:10px'})
        )
        self.fields['actions_class'] = forms.ChoiceField(
            choices=self.actions_class_choices,
            widget=forms.Select(attrs={'style': 'font-size:10px'})
        )
        self.fields['signal_kwargs'] = forms.CharField(required=False)

    @property
    def variables_class_choices(self):
        variable_classes = list(classes_from_module_list(modules_with_variables()))

        return zip(variable_classes, variable_classes)

    @property
    def actions_class_choices(self):
        action_classes = list(classes_from_module_list(modules_with_actions()))

        return zip(action_classes, action_classes)

    class Meta:
        model = BusinessRuleSet
        fields = [
            'name',
            'enabled',
            'notes',
            'signal',
            'signal_kwargs',
            'variables_class',
            'actions_class',
            'stop_on_first_trigger'
        ]


class ConditionAdminForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = [
            'group',
            'property_method',
            'property_kwargs',
            'comparison_operator',
            'value'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        comparison_choices = ['op.eq', 'op.ne']

        if kwargs.get('instance') is not None:
            instance = kwargs['instance']
            properties = instance.variable_properties

            self.fields['property_method'] = forms.ChoiceField(
                choices=zip(properties, properties)
            )

            self.fields['property_kwargs'] = forms.CharField()
            self.fields['value'] = forms.CharField(required=False)

            comparison_choices = instance.comparison_operator_choices

        self.fields['comparison_operator'] = forms.ChoiceField(
            choices=zip(comparison_choices, comparison_choices)
        )


class ActionAdminForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = [
            'block',
            'action_method',
            'action_kwargs'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['action_kwargs'] = forms.CharField(required=False)

        if kwargs.get('instance') is not None:
            instance = kwargs['instance']

            self.fields['action_method'] = forms.ChoiceField(
                choices=zip(instance.action_method_choices, instance.action_method_choices)
            )
