import pusher
from django.conf import settings


class Notifier(object):

    @classmethod
    def notify(cls, channels, event_name, data, socket_id=None):

        if settings.NOTIFICATIONS_ENABLED is True:
            cls.get_client().trigger(
                channels, event_name, data, socket_id=None)

    @classmethod
    def get_client(cls):
        pusher_client = pusher.Pusher(
          app_id='375636',
          key='6b354dd0159c5d4555a9',
          secret='48b3c45452c642ec68d7',
          cluster='us2',
          ssl=True
        )
        return pusher_client
