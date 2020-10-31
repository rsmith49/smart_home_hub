from flask import Flask, request

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run()
