import json
import urllib.request

import swagger_client as sw
from flask import session, current_app, redirect
from flask_login import login_user, logout_user

from web.modules.entity import LoginUser


def redirect_(path):
    return redirect(current_app.config.get('WEB_HOST') + path)


def login_user_(access_token):
    session['token'] = access_token
    my_api = sw.MyApi(sw.ApiClient(host=current_app.config.get('API_HOST'),
                                   header_name='Authorization',
                                   header_value='JWT %s' % session['token']))
    login_user(LoginUser(profile=my_api.my_profile_get()))
    # ログイン時にアンデリの通知カウントをリセットする
    if 'notify_count' in session:
        session.pop('notify_count')


def logout_user_():
    logout_user()
    if 'token' in session:
        session.pop('token')


def login_user_dummy():
    req = urllib.request.Request(url=current_app.config.get('API_HOST') + '/debug/login',
                                 method='POST')
    resp = urllib.request.urlopen(req)
    if resp.status == 200:
        response = resp.read().decode("utf-8")
        login_user_(access_token=json.loads(response)['access_token'])
