import swagger_client as sw
from flask import url_for, current_app, Blueprint, Response, jsonify

from web.views.common import login_user_dummy, redirect_

blueprint = Blueprint('debug', __name__)


@blueprint.route('/login')
def debug_login() -> Response:
    """ローカル実行用ログイン"""
    if current_app.config.get('DEBUG'):
        login_user_dummy()
    return redirect_(url_for('front.home'))


@blueprint.route('/healthcheck')
def debug_health_check() -> Response:
    """ヘルスチェック"""
    health = {}
    try:
        auth_api = sw.AuthApi(sw.ApiClient(current_app.config.get('API_HOST')))
        auth = sw.Authenticate()
        auth.key = 'anonymous'
        auth.secret = 'anonymous'
        auth.device = None
        auth.trid = None
        result = auth_api.authenticate_post(authenticate=auth)
        assert result.access_token
        health['api'] = 'ok'
    except Exception as ex:
        current_app.logger.error('healthcheck(api): %s', ex)
        return jsonify({'status': 'ng', 'message': 'failed to api check.'}), 500
    health['status'] = 'ok'
    return jsonify(health)
