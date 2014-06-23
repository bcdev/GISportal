from flask import Blueprint, jsonify, current_app

portal_actions = Blueprint('portal_actions', __name__)

@portal_actions.route('/retrieve_actions', methods=['GET'])
def retrieve_actions():
    print('retrieving actions')
    action_registry = current_app.config.get('ACTION_REGISTRY')
    return jsonify(action_registry=action_registry)