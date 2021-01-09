import requests

from abc import ABCMeta

from smart_home_hub.device.base_device import DeviceAction


class Tmp(DeviceAction, metaclass=ABCMeta):

    def open_content(self, app_id, content_id, media_type):
        """
        Helper method that sends a request to Roku to play the media specified
        :param app_id: ID of the app
                       (Netflix is 12)
        :param content_id: Content ID for the content to play
                           (this will be hard af)
                           (Netflix episodes & shows can be found online manually)
        :param media_type: One of season, episode, movie, short-form, special, live
        """
        requests.post(
            self.device.config['ip'] + f'launch/{app_id}',
            params={
                'contentID': content_id,
                'mediaType': media_type
            }
        )
