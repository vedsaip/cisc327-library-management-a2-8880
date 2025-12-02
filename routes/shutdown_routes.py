
from flask import Blueprint, request, abort

shutdown_bp = Blueprint('shutdown', __name__)

@shutdown_bp.route('/shutdown', methods=['POST'])
def shutdown():
    if not request.environ.get('werkzeug.server.shutdown'):
        abort(404)
    request.environ.get('werkzeug.server.shutdown')()
    return 'Server shutting down...'
