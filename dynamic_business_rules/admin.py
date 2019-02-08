from django.contrib import admin

import nested_admin

from .models import BusinessRuleSet, RuleBlock, ConditionSet, Condition, Action
from .forms import BusinessRuleSetAdminForm, ConditionAdminForm, ActionAdminForm


class ConditionInline(nested_admin.NestedStackedInline):
    model = Condition
    extra = 0
    form = ConditionAdminForm
    fieldsets = [
        (None, {
            "fields": [
                ('property_method', 'comparison_operator', 'value'),
                'property_kwargs'
            ]
        })
    ]


class ConditionSetInline(nested_admin.NestedStackedInline):
    model = ConditionSet
    inlines = [ConditionInline]
    extra = 0
    fieldsets = [
        (None, {
            "fields": [('name', 'combination_rule', 'parent_condition')]
        })
    ]


class ActionInline(nested_admin.NestedStackedInline):
    model = Action
    extra = 0
    form = ActionAdminForm


class RuleBlockInline(nested_admin.NestedStackedInline):
    model = RuleBlock
    inlines = [ConditionSetInline, ActionInline]
    extra = 0
    fieldsets = [
        (None, {
            "fields": [('name', 'enabled')]
        })
    ]


@admin.register(BusinessRuleSet)
class BusinessRuleSetAdmin(nested_admin.NestedModelAdmin):
    inlines = [RuleBlockInline]
    form = BusinessRuleSetAdminForm
    fieldsets = [
        (None, {
            "fields": [
                ('name', 'enabled'),
                'notes',
                ('signal', 'signal_kwargs'),
                ('variables_class', 'actions_class'),
                'stop_on_first_trigger',
            ],
        })
    ]
    list_display = [
        'name',
        'signal',
        'signal_kwargs',
        'variables_class',
        'actions_class'
    ]
