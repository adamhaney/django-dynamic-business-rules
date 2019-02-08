from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from django.db import models
from django.utils.module_loading import import_string
from django.contrib.postgres.fields import JSONField


class BaseModel(TimeStampedModel):
    """
    By default all models should have timestamp info and history
    """
    class Meta:
        abstract = True

    history = HistoricalRecords(inherit=True)


class BusinessRuleSet(BaseModel):
    """
    A collection of rules that are evaluated in order, if
    stop_on_first_trigger is true the rule set will short circuit as
    soon as the first rule set evaluates to true, otherwise all rules
    in the rule set will be evaluated.
    """
    enabled = models.BooleanField(
        default=False,
        help_text="Should this rule set execute?"
    )
    name = models.CharField(
        max_length=140,
        help_text="A descriptive name so we know what this ruleset does"
    )
    notes = models.TextField(
        null=True,
        blank=True
    )
    signal = models.CharField(
        max_length=240,
        help_text="import path of a signal that shoudl fire this ruleset",
    )
    signal_kwargs = JSONField(
        default={},
        blank=True,
        help_text="kwargs to pass to signal registration ({'sender': 'Model' would be a common pattern here})"
    )
    stop_on_first_trigger = models.BooleanField(
        default=False,
        help_text="Should this ruleset stop on the first triggered block?"
    )
    variables_class = models.CharField(
        max_length=140,
        help_text="Import path and class for Variables"
    )
    actions_class = models.CharField(
        max_length=140,
        help_text="Import path and class for Actions"
    )

    def __str__(self):
        return self.name

    @property
    def variable_class_object(self):
        return import_string(self.variables_class)

    @property
    def action_class_object(self):
        return import_string(self.actions_class)

    def signal_callback(self, *args, **kwargs):
        if not self.enabled:
            return

        # NOTE: Variables and Action classes need to accept args and kwargs
        # from signal callback as arguments to their constructor
        variables_instance = self.variable_class_object(*args, **kwargs)
        actions_instance = self.action_class_object(*args, **kwargs)

        for rule_block in self.rule_blocks.filter(enabled=True):
            result = rule_block.run(variables_instance, actions_instance)
            if result is True and self.stop_on_first_trigger:
                return


class RuleBlock(BaseModel):
    rule_set = models.ForeignKey(
        BusinessRuleSet,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=140,
        help_text="Description of what this block does"
    )
    enabled = models.BooleanField(
        default=False,
        help_text="Should this block be executed as a part of the rule set?"
    )

    def __str__(self):
        return self.name

    def run(self, variables_instance, actions_instance):
        if self.all_conditions_true(variables_instance, actions_instance):
            self.run_actions(variables_instance, actions_instance)
            return True
        else:
            return False

    def all_conditions_true(self, variables_instance):
        return all(map(lambda group: group.evaluate(variables_instance), self.condition_sets.all()))

    def run_actions(self, variables_instance, actions_instance):
        for action in self.actions.all():
            action.run(variables_instance, actions_instance)


class ConditionSet(BaseModel):
    block = models.ForeignKey(
        RuleBlock,
        on_delete=models.CASCADE,
        related_name='condition_sets'
    )
    name = models.CharField(
        help_text="A descriptive name for this group of conditions",
        max_length=140
    )
    parent_condition = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='child_condition_sets',
        on_delete=models.CASCADE
    )
    combination_rule = models.CharField(
        max_length=10,
        choices=[
            ('any', 'any'),
            ('all', 'all')
        ],
        default='all'
    )

    def __str__(self):
        return self.name

    def evaluate(self, variables_instance):
        if self.combination_rule == 'any':
            return any(self.depth_first_evaluate_results(variables_instance))
        if self.combination_rule == 'all':
            return any(self.depth_first_evaluate_results(variables_instance))

        raise ValueError('could not evaluate ConditionSet with combination rule %s', self.combination_rule)

    def depth_first_evaluate_results(self, variables_instance):
        return self.child_set_results(variables_instance) + self.child_condition_results(variables_instance)

    def child_set_results(self, variables_instance):
        return list(
            map(
                lambda condition_set: condition_set.evaluate(variables_instance),
                self.child_condition_sets.all()
            )
        )

    def child_condition_results(self, variables_instance):
        return list(map(lambda condition: condition.evaluate(variables_instance), self.conditions.all()))


class Condition(BaseModel):
    group = models.ForeignKey(
        ConditionSet,
        on_delete=models.CASCADE,
        related_name='comditions'
    )
    property_method = models.CharField(
        max_length=140,
        null=True,
        blank=True
    )
    property_kwargs = JSONField(
        default={},
        help_text="kwargs to pass to the method that gets the left hand side of our comparison",
        blank=True
    )
    comparison_operator = models.CharField(
        max_length=140
    )
    value = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        if self.property_method is None:
            return '-'

        return self.property_method

    @property
    def operator_instance(self):
        return import_string(self.comparison_operator)

    @property
    def variable_class_object(self):
        return self.group.block.rule_set.variable_class_object

    @property
    def property_method_instance(self):
        if self.property_method and hasattr(self.variable_class_object, self.property_method):
            return getattr(self.variable_class_object, self.property_method)

    @property
    def comparison_operator_choices(self):
        if self.property_method_instance and hasattr(self.property_method_instance, 'operators'):
            return self.property_method_instance.operators
        else:
            return self.get_default_comparison_operators()

    @staticmethod
    def get_default_comparison_operators():
        return [
            'operator.lt',
            'operator.le',
            'operator.eq',
            'operator.ne',
            'operator.ge',
            'operator.gt',
            'operator.not_',
            'operator.truth',
            'operator.is',
            'operator.is_not',
            'str.startswith',
            'str.endswith'
        ]

    @property
    def variable_properties(self):
        return [
            method
            for method
            in dir(self.variable_class_object)
            if not method.startswith('__')
        ]

    def evaluate(self, variable_instance):
        return self.operator_instance(
            getattr(variable_instance, self.property_method)(**self.property_kwargs),
            self.value
        )


class Action(BaseModel):
    block = models.ForeignKey(
        RuleBlock,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    action_method = models.CharField(
        max_length=140
    )
    action_kwargs = JSONField(
        default={},
        help_text="kwargs to pass action method"
    )

    def __str__(self):
        return self.action_method

    def run(self, variables_instance, actions_instance):
        # All action methods need to take variables as their first argument
        getattr(actions_instance, self.action_method)(variables_instance, self.action_kwargs)

    @property
    def action_class_object(self):
        return self.block.rule_set.action_class_object

    @property
    def action_method_choices(self):
        return [
            method
            for method
            in dir(self.action_class_object)
            if not method.startswith('__')
        ]
