class SalesTransitionVariables(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_spot_id(self, *args, **kwargs):
        return self.kwargs.instance.spot.id

    def get_spot_market_id(self, *args, **kwargs):
        return self.kwargs.instance.spot.market.id

    def get_source_category(self, *args, **kwargs):
        return self.kwargs.instance.source.category

    def get_source_name(self, *args, **kwargs):
        return self.kwargs.instance.source.name

    def get_target_category(self, *args, **kwargs):
        return self.kwargs.instance.target.category

    def get_target_name(self, *args, **kwargs):
        return self.kwargs.instance.target.name

    get_spot_id.operators = [
        'class.operator'
    ]
