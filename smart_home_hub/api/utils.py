from flask import request
from flask.views import MethodView
from flask_api import status
from marshmallow import fields

from smart_home_hub.utils.env_consts import API_KEY
from smart_home_hub.utils.utils import titleize
from smart_home_hub.utils.argmap_utils import FIELD_TO_STR_MAP


def argmap_resp_obj(argmap):
    """
    Returns a JSON compatible argmap (instead of using marshmallow fields, use
    dicts with string keys).
    :param argmap: Dict containing string keys to marshmallow field values
    :return: A dict with string keys to dict values
    """

    def set_keys(curr_argmap, curr_json_argmap):
        """
        Helper method to handle the recursion involved with duplicating
        the dict structure across the whole tree
        """
        for key, val in curr_argmap.items():
            if isinstance(val, fields.Field):
                curr_json_argmap[key] = {
                    'required': val.required,
                    'datatype': FIELD_TO_STR_MAP[type(val)]
                }

                if val.missing != fields.missing_:
                    curr_json_argmap[key]['default'] = val.missing

                # Adding the metadata properties for each arg
                for meta_prop in [
                    # Informational metadata
                    'description', 'label'
                ]:
                    if meta_prop in val.metadata:
                        curr_json_argmap[key][meta_prop] = val.metadata[meta_prop]

                # If no label as metadata, just use titleized arg name
                if 'label' not in curr_json_argmap[key]:
                    curr_json_argmap[key]['label'] = titleize(key)

            elif type(val) is list:
                # TODO: Support lists
                pass

            elif type(val) is dict:
                curr_json_argmap[key] = {}
                set_keys(curr_argmap[key], curr_json_argmap[key])

            else:
                raise ValueError(
                    'Invalid argmap value: {} (type {})'.format(
                        val,
                        type(val)
                    )
                )

    json_argmap_ = {}
    set_keys(argmap, json_argmap_)
    return json_argmap_


def get_context():
    """
    Retrieves the saved context for the current request.
    :return: A dict representing the current context
    """
    # TODO: Make this work


class APIInvalidError(Exception):
    """
    Error to raise in order to exit early from a request, and return the
    appropriate error code and message
    """

    message_map = {
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_404_NOT_FOUND: "Not Found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Method Not Allowed",
        status.HTTP_406_NOT_ACCEPTABLE: "Not Acceptable",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        None: ""
    }

    def __init__(self, status_code=None, message=None, payload=None):
        Exception.__init__(self)
        if message is None:
            self.message = self.message_map[status_code]
        else:
            self.message = (self.message_map[status_code] + ": " + message)
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = self.status_code
        rv['message'] = self.message
        return rv


class APIResource(MethodView):

    def authenticate(self):
        """
        Authenticates the request based on an API key being present in
        either the headers or query parameters
        :return: True if api key passes, otherwise raises APIInvalidError
        """
        try:
            if request.headers['api_key'] == API_KEY:
                return True
        except KeyError:
            # API Key not in headers
            pass

        try:
            if request.args['api_key'] == API_KEY:
                return True
        except KeyError:
            # API Key not in query params
            pass

        raise APIInvalidError(status.HTTP_401_UNAUTHORIZED)
