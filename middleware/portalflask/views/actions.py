from functools import wraps
from flask import Blueprint, jsonify, current_app, g
from portalflask import app

portal_actions = Blueprint('portal_actions', __name__)

@portal_actions.route('/retrieve_actions', methods=['GET'])
def retrieve_actions():
    print('retrieving actions')
    action_registry = current_app.config.get('ACTION_REGISTRY')
    return jsonify(action_registry=action_registry)


def check_for_permission(roles):
    def decorator(f):
        @wraps(f)
        def check_permission(*args, **kwargs):
            if g.user is not None:
                for group in g.user.groups:
                    if group.group_name in roles:
                        return f(*args, **kwargs)

            print('Trying to execute unauthorised method!')
            return jsonify(user='None')
        return check_permission

    return decorator
