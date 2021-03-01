import json
import requests

TODO = """
# For accessing a list of movies given Authorization
URL = 'https://api.reelgood.com/v3.0/content/userlisting/movies?availability=all&hide_seen=true&hide_tracked=false&hide_watchlisted=false&imdb_end=10&imdb_start=0&region=us&rg_end=100&rg_start=0&skip=0&sort=0&take=50&year_end=2021&year_start=1900'
URL = '/v3.0/content/userlisting/movies'
# Shows
URL = '	https://api.reelgood.com/v3.0/content/userlisting/shows/both?availability=all&genre=5&hide_seen=false&hide_tracked=false&hide_watchlisted=false&imdb_end=10&imdb_start=0&region=us&rg_end=100&rg_start=0&skip=0&sort=0&take=50&year_end=2021&year_start=1900'
"""

BASE_API_URL = 'https://api.reelgood.com/v3.0'
BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'x-platform': 'web',
    'Content-Type': 'application/json',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Origin': 'https://reelgood.com',
    'TE': 'Trailers'
}
SERVICE_CONVERSION_MAP = {
    'amazon_prime': 'prime',
    'hulu_plus': 'hulu'
}


class RGClient:
    """
    This class creates a client to access Reelgood data for the account
    specified. It can then retrieve the content ID for shows, movies and
    episodes based on the title. It can also return watch lists created by the
    user.
    """
    def __init__(self, email=None, password=None, cred_file=None):
        """
        :param email: Email to use for creating the client
        :param password: Password to use for creating the client
        :param cred_file: Optional credential file, to retrieve the credentials
                          without explicitly passing email and password
        """
        # TODO: Make this able to be used without an account
        # TODO: Maybe add a cooldown for requests (have like a "time since last request")
        if cred_file is not None:
            with open(cred_file) as credential_file:
                creds = json.load(credential_file)

            self.email = creds['email']
            self.password = creds['password']

        elif email is not None and password is not None:
            self.email = email
            self.password = password

        else:
            raise ValueError('Must specify one of email & password, or cred_file')

        self.access_token = None
        self._refresh_access_token()

    def get_movie_viewing_id(self, rg_id):
        """
        Returns a dict of services to their ID's for the movie given by the ID

        :param rg_id:
        :return: A dict of the form:
                 {
                   "hulu": movie ID,
                   "netflix": movie ID,
                   ...
                 }
        """
        info = self.get_content_info('m', rg_id)

        return self._get_streaming_id_map('movie', info)

    def get_show_viewing_id(self, rg_id):
        """
        Returns a dict of services to their ID's for the recommended episode
        of the specified show.

        :param rg_id:
        :return: A dict of the form:
                 {
                   "hulu": episode ID,
                   "netflix": episode ID,
                   ...
                 }
        """

        info = self.get_content_info('s', rg_id)

        if info.get('recommended_episode'):
            recommended_id = info['recommended_episode']['episode_id']
        else:
            min_seq_num = 1000
            recommended_id = None

            for ep in info['episodes'].values():
                if ep['sequence_number'] < min_seq_num:
                    min_seq_num = ep['sequence_number']
                    recommended_id = ep['id']

        episode = info['episodes'][recommended_id]

        return self._get_streaming_id_map('episode', episode)

    def get_content_info(self, content_type, rg_id):
        """
        Retrieves the dict of content info from RG for a given ID

        :param content_type: Either show ir movie ("s" | "m")
        :param rg_id:
        :return: A dict containing all of the properties returned by the API
        """
        self._validate_content_type(content_type)
        content_type_str = 'show' if content_type == 's' else 'movie'

        return self._make_request(
            requests.get,
            f'/content/{content_type_str}/{rg_id}',
            params={
                'interaction': 'true',
                'region': 'us'
            }
        )

    def query_content(self, content_type, title):
        """
        Helper method to use as a basis for querying shows and movies based on
        the title

        :param content_type: Either show or movie ("s" | "m")
        :param title: Title of the content to query
        :return: A list of the content type we tried to search for
        """
        self._validate_content_type(content_type)

        results = self._make_request(
            requests.get,
            '/content/search/content',
            params={
                'page': 1,
                'pageSize': 50,
                'region': 'us',
                'take': 50,
                'terms': title
            }
        )['items']

        return [
            content for content in results
            if content['content_type'] == content_type
        ]

    def _make_request(self, method, endpoint, **request_args):
        """
        A helper method to make and return an authorized request to the API

        :param method: The requests method to use (requests.post, etc.)
        :param endpoint: The relative endpoint path to make the request to
        :param request_args: Any additional keyword args to pass to `method`
        :return: The JSON of the response
        """
        def get_resp():
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Host': 'api.reelgood.com',
                **BASE_HEADERS
            }

            # Copying in case we have to retry the request, so we don't lose
            # the original headers
            new_args = request_args.copy()

            if 'headers' in request_args:
                headers.update(new_args.pop('headers'))

            return method(
                BASE_API_URL + endpoint,
                headers=headers,
                **new_args
            )

        resp = get_resp()
        if resp.status_code == 401:
            self._refresh_access_token()
            resp = get_resp()

        resp.raise_for_status()
        return resp.json()

    def _refresh_access_token(self):
        """
        Helper method to refresh the access token
        """
        resp = requests.post(
            'https://reelgood.com/login',
            json={
                'email': self.email,
                'password': self.password,
                'mixpanel_id': '177e7eda3ac6d-01f4de517e87dd8-44596a-1fa400-177e7eda3ad14c',
                'eventData': {
                    'product': 'web',
                    'platform': 'desktop',
                    'current_url': '/login'
                }
            },
            headers={
                'Host': 'reelgood.com',
                'Referer': 'https://reelgood.com/login',
                'Content-Length': '208',
                **BASE_HEADERS
            }
        )
        resp.raise_for_status()

        self.access_token = resp.json()['access_token']

    @staticmethod
    def _validate_content_type(content_type):
        if content_type not in ['s', 'm']:
            raise ValueError('content_type should be one of "s", "m"')

    @staticmethod
    def _get_streaming_id_map(content_type, content_info):
        """
        Helper method to retrieve the map of the form
        {
          "hulu": streaming ID,
          "netflix": streaming ID,
          ...
        }
        """
        streaming_map = {}

        for source in content_info['availability']:
            try:
                if source['source_name'] in SERVICE_CONVERSION_MAP:
                    source_name = SERVICE_CONVERSION_MAP[source['source_name']]
                else:
                    source_name = source['source_name'].lower()

                streaming_map[source_name] = source['source_data']['references']['web'][f'{content_type}_id']

            except (KeyError, TypeError):
                # If it doesn't have a source link, just don't include it
                pass

        return streaming_map
