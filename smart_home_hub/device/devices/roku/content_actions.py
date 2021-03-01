import random
import requests

from abc import ABCMeta
from marshmallow import fields

from smart_home_hub.device.base_device import DeviceAction
from smart_home_hub.utils.config import load_config

# TODO: Add a contentID search for things that support it, like youtube


class ContentAction(DeviceAction, metaclass=ABCMeta):

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

    @staticmethod
    def channel_id_map():
        """
        Loads the config for channel_id_map.json
        :return: A dict containing a map of the channel names to ID's
        """
        return load_config('roku/content/channel_id_map.json')


class RGPlayContent(ContentAction, metaclass=ABCMeta):
    """
    Base class for playing content (so that the command can be movie or show)
    """
    _content_type = None

    def argmap(self) -> dict:
        return {
            'title': fields.Str(
                required=True,
                voice_ndx=1
            ),
            'service': fields.Str(
                voice_ndx=0
            )
        }

    def perform(self):
        if self._content_type not in ['movie', 'show']:
            raise NotImplementedError('Must set _content_type')

        content_str = 'm' if self._content_type == 'movie' else 's'

        title = self.args['title']
        service = self.args.get('service')

        channel_id_map = self.channel_id_map()

        content_list = self.device.rg_client.query_content(content_str, title)

        if len(content_list) == 0:
            self.set_msg(
                f'Could not find {self._content_type} with title {title}'
            )
            return

        if self._content_type == 'movie':
            service_id_map = self.device.rg_client.get_movie_viewing_id(
                content_list[0]['id']
            )
        else:
            service_id_map = self.device.rg_client.get_show_viewing_id(
                content_list[0]['id']
            )

        if service is None:
            services = [
                s for s in service_id_map.keys()
                if s in channel_id_map
            ]

            if len(services) == 0:
                self.set_msg(f"Could not find compatible service")
                return

            service = services[0]

        self.open_content(
            channel_id_map[service],
            service_id_map[service],
            self._content_type
        )


class PlayMovie(RGPlayContent):
    _name = 'play_movie'
    _desc = 'Plays a movie on the Roku given a title (if found)'
    _content_type = 'movie'


class PlayShow(RGPlayContent):
    _name = 'play_show'
    _desc = 'Plays a show on the Roku given a title (if found)'
    _content_type = 'show'


class PlayContent(ContentAction):
    _name = 'play_content'
    _desc = 'Plays a specific piece of content given by service and name'

    def argmap(self) -> dict:
        return {
            'service': fields.Str(
                required=True,
                voice_ndx=0
            ),
            'content': fields.Str(
                required=True,
                voice_ndx=1
            )
        }

    def perform(self):
        service = self.args['service']
        content = self.args['content']

        content_id_map = load_config('roku/content/content_id_map.json')
        try:
            self.open_content(
                self.channel_id_map()[service],
                content_id_map[service][content],
                'episode'
            )
        except KeyError:
            self.set_msg(
                f'Could not find content for channel {service} and content {content}'
            )


class PlayRandom(ContentAction):
    _name = 'play_random'
    _desc = 'Plays a random episode from the dict of shows to eps available'

    def argmap(self) -> dict:
        return {
            'show': fields.Str(
                required=False,
                missing='any',
                voice_ndx=0
            )
        }

    def perform(self):
        ep_ranges_map = load_config('roku/content/random_episode_ranges.json')

        if self.args['show'] == 'any':
            channel_name = random.choice(list(ep_ranges_map.keys()))
            show_name = random.choice(list(ep_ranges_map[channel_name].keys()))
        else:
            show_name = self.args['show'].lower()
            channel_name = None
            for channel in ep_ranges_map:
                if self.args['show'] in ep_ranges_map[channel]:
                    channel_name = channel

            if channel_name is None:
                self.set_msg(f'No show found for {show_name}')
                return

        ndx_lists = [
            list(range(
                ep_limits[0],
                ep_limits[1] + 1
            ))
            for ep_limits in ep_ranges_map[channel_name][show_name]
        ]
        ndxs = [ndx for ndx_list in ndx_lists for ndx in ndx_list]

        self.open_content(
            self.channel_id_map()[channel_name],
            random.choice(ndxs),
            'episode'
        )
