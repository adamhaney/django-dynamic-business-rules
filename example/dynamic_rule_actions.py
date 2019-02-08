from slackclient import SlackClient

from django.conf import settings


class SalesTransitionActions(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def send_slack_message(
            self,
            username="Dynamic Sales Transition Bot",
            channel="@adamhaney",
            text="",
            *args,
            **kwargs
    ):
        slack_client = kwargs.pop('slack_client', SlackClient(settings.SLACK_API_TOKEN))
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            icon_url="https://i.imgur.com/uxUK5.jpg",
            username=username,
            text=text,
        )

    def create_system_change_log(self, *args, **kwargs):
        pass
