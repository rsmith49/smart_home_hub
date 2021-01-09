import json
import os
import sys

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from webargs.flaskparser import parser

sys.path.append(os.getcwd())

from smart_home_hub.api.utils import APIInvalidError, get_context
from smart_home_hub.api.device_resource import device_resp_obj, action_resp_obj
from smart_home_hub.device import device_class_map

app = Flask(__name__)


@app.errorhandler(APIInvalidError)
def error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/devices', methods=['GET'])
def devices():
    """
    Responds with a list of all available devices
    (does not include context)
    """
    # TODO: Maybe include context here (could have context applicable to
    #       multiple devices)
    return jsonify([
        device_resp_obj(device_cls())
        for device_cls in device_class_map.values()
    ]), 200


@app.route('/devices/<device_name>', methods=['GET'])
def device(device_name):
    """
    Responds with the device info and actions for a specific device
    (includes context)
    """
    try:
        device_cls = device_class_map[device_name]
    except KeyError:
        raise APIInvalidError(404)

    context = get_context()
    d = device_cls(context=context)

    return jsonify(device_resp_obj(d)), 200


@app.route('/devices/<device_name>/<action_name>', methods=['GET', 'POST'])
def action(device_name, action_name):
    """
    Either executes the action with the given arguments (POST), or
    Retrieves the action and its arg map based on the context
    """
    try:
        device_cls = device_class_map[device_name]
    except KeyError:
        raise APIInvalidError(404, 'No device found')

    context = get_context()
    d = device_cls(context=context)

    try:
        a = d.action_map()[action_name]
    except KeyError:
        raise APIInvalidError(404, 'No action found')

    if request.method == 'GET':
        return jsonify(action_resp_obj(a)), 200
    else:
        a.init_args(**parser.parse(
            argmap=a.argmap(),
            location='json',
            error_status_code=400
        ))
        a.perform()

        return jsonify(a.response()), 200


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """
    Shuts down the API (since there is no legit way to kill the thread)
    Pulled from https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
    """
    func = request.environ.get('werkzeug.server.shutdown')

    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

    return 'Server shutting down...', 200


# Registering Errors for easier readability in UI
@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    data_dict = {
        "status": e.code,
        "name": e.name,
        "description": e.description
    }

    if hasattr(e, 'data') and 'messages' in e.data:
        data_dict['errors'] = []

        for _, err_msgs in e.data['messages'].items():
            data_dict['errors'].extend([
                '{}: {}'.format(key, msg)
                for key, msgs in err_msgs.items() for msg in msgs
            ])

    response.data = json.dumps(data_dict)
    response.content_type = "application/json"
    return response


if __name__ == '__main__':
    app.run()
