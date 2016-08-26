import os
import re
from datetime import datetime, timedelta, date
from logging import Formatter
from logging.handlers import RotatingFileHandler
from urllib import parse
from urllib.error import HTTPError, URLError

import swagger_client as sw
from datadog import statsd
from flask import Flask, current_app, render_template, session, g, url_for, request
from flask_login import LoginManager
from flask_session import Session
from flask_wtf.csrf import CsrfProtect
from swagger_client.rest import ApiException

from web.modules.entity import LoginUser
from web.modules.utils import check_device, check_trid
from web.views import front, creator, ajax, debug
from web.views.common import redirect_

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
if 'PROFILE' in os.environ:
    app.config.from_envvar('PROFILE')
else:
    app.config.from_pyfile('config.py')
app.permanent_session_lifetime = timedelta(days=360)

sess = Session()
sess.init_app(app)
sess.permanent = True

csrf = CsrfProtect()
csrf.init_app(app)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Logging
app.debug_log_format = '%(asctime)s\t[%(levelname)s]\t%(message)s'
log_file = app.config.get('LOG_PATH')
file_handler = RotatingFileHandler(log_file, backupCount=3, maxBytes=100000)
file_handler.setFormatter(Formatter('%(asctime)s\t[%(levelname)s]\t%(message)s'))
file_handler.setLevel(app.config.get('LOG_LEVEL'))
app.logger.addHandler(file_handler)
app.logger.setLevel(app.config.get('LOG_LEVEL'))

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect_(url_for('front.home'))


def refresh_token(device_type):
    if 'token' in session:
        '''認証済みの場合は有効性チェック'''
        my_api = sw.MyApi(sw.ApiClient(host=app.config.get('API_HOST'),
                                       header_name='Authorization',
                                       header_value='JWT %s' % session['token']))
        try:
            my_api.my_profile_get()
        except ApiException as err:
            '''有効でない場合はトークンを破棄'''
            if err.status == 401:
                session.pop('token')
            else:
                return render_template('plain.html', message='server error')
    '''セッションにトークンがない場合は匿名トークンを発行'''
    if 'token' not in session:
        auth_api = sw.AuthApi(sw.ApiClient(app.config.get('API_HOST')))
        auth = sw.Authenticate()
        auth.key = 'anonymous'
        auth.secret = 'anonymous'
        auth.device = device_type
        auth.trid = check_trid(cookies=request.cookies)
        result = auth_api.authenticate_post(authenticate=auth)
        session['token'] = result.access_token
    g.api = sw.ApiClient(host=app.config.get('API_HOST'), header_name='Authorization',
                         header_value='JWT %s' % session['token'])


@login_manager.user_loader
def load_user(user_id=None):
    try:
        if 'api' not in g:
            g.api = sw.ApiClient(host=app.config.get('API_HOST'))
        my_api = sw.MyApi(api_client=g.api)
        user = LoginUser(my_api.my_profile_get())
        if str(user.id) == user_id:
            return user
        else:
            return None
    except(HTTPError, URLError, ApiException) as detail:
        print(detail)
        return None


@app.context_processor
def inject_user():
    return {
        'google_analytics': current_app.config.get('GOOGLE_ANALYTICS'),
        'google_tag_manager': current_app.config.get('GOOGLE_TAG_MANAGER'),
        'gmo_shop_id': current_app.config.get('GMO_SHOP_ID'),
        'gmo_script_url': current_app.config.get('GMO_SCRIPT_URL'),
        'faq_site_url': current_app.config.get('FAQ_SITE_URL')
    }


@app.before_request
def before_request():
    if not request.path.startswith('/static/') \
            and not request.path.startswith('/debug/'):
        statsd.increment('web.page_views')
        refresh_token(device_type=check_device(request.user_agent))


@app.errorhandler(404)
def page_not_found(error=None):
    print('404: %s' % error)
    return render_template('plain.html', message='page not found'), 404


@app.errorhandler(400)
def bad_request(error=None):
    print('400: %s' % error)
    return render_template('plain.html', message='bad request'), 404


@app.errorhandler
def server_error(error=None):
    print('Unexpected Error: %s' % error)
    return render_template('plain.html', message='server error'), 500


app.register_blueprint(front.blueprint)
app.register_blueprint(creator.blueprint, url_prefix='/_creator')
app.register_blueprint(ajax.blueprint, url_prefix='/api')
app.register_blueprint(debug.blueprint, url_prefix='/debug')


@app.template_filter()
def to_cdn(path, prefix='common'):
    """CDNのURLに変換して返却"""
    # TODO common配下をローカルで確認する場合はこちらを使用する
    if prefix == 'common' and current_app.config.get('DESIGN'):
        return '/static/cdn/' + path
    # common配下をCDNから取得する場合はこちらを使用する
    if path:
        # if path.startswith('theme'):
        #     cache = datetime.today().strftime('%y%m%d%H')  # TODO 1時間以内に反映
        #     return app.config.get('CDN_BASE_URL') + '%s/%s?%s' % (prefix, parse.quote(path), cache,)
        # else:
        return app.config.get('CDN_BASE_URL') + '%s/%s' % (prefix, parse.quote(path),)
    else:
        # パスがない場合はダミー画像に置き換える
        if prefix == 'project':
            return app.config.get('CDN_BASE_URL') + 'common/image/noimage/project.png'
        elif prefix == 'profile':
            return app.config.get('CDN_BASE_URL') + 'common/image/noimage/profile.png'
        else:
            return app.config.get('CDN_BASE_URL') + 'common/image/noimage/item.png'


@app.template_filter()
def format_date(time: datetime):
    """日付フォーマット"""
    return '%s.%s.%s' % (time.year, time.month, time.day,)


@app.template_filter()
def format_datemonth(time: datetime):
    """日付フォーマット"""
    return '%s年%s月' % (time.year, time.month,)


@app.template_filter()
def format_datetime(time: datetime):
    """日付フォーマット"""
    if time:
        return time.strftime('%Y/%m/%d %H:%M')
    else:
        return ''


@app.template_filter()
def codec(value: str, code_type: str):
    if code_type == 'is_approval':
        if value == 0: return '未承認'
        if value == 1: return '承認済'
        if value == 2: return '非承認'
        if value == 3: return '未申請'
    if code_type == 'public_status':
        if value == 1: return '公開前'
        if value == 2: return '公開中'
        if value == 3: return '終了'
        if value == 4: return '非公開'
    if code_type == 'type':
        if value == 1: return '実施確約型'
        if value == 2: return 'チャレンジ型'
        if value == 3: return 'プレオーダー型'
    if code_type == 'target_status':
        if value == 0: return '目標設定なし'
        if value == 1: return '未達成'
        if value == 2: return '達成'
    if code_type == 'support_status':
        if value == 1: return '決済未完了'
        if value == 2: return 'キャンセル'
        if value == 3: return '決済完了'
    if code_type == 'payment_type':
        if value == 'credit': return 'クレジットカード'
        if value == 'cvs': return 'コンビニ'
        if value == 'payeasy': return 'Pay-easy'


@app.template_filter()
def remaining_days(project_end_date: datetime) -> int:
    """
    プロジェクトの残り日数計算

    :param project_end_date: プロジェクト終了日
    :return: 残り日数
    """
    return max(0, (project_end_date.date() - datetime.today().date()).days)


@app.template_filter()
def remaining_days_rate(project) -> int:
    """
    プロジェクトの残り日数計算(割合)

    :param project: プロジェクト
    :return: 残り日数(%)
    """
    total_days = (project.end_time.date() - project.start_time.date()).days
    passing_days = (datetime.today().date() - project.start_time.date()).days
    if 0 < passing_days < total_days:
        return int((passing_days / total_days) * 100)
    else:
        return 100


@app.template_filter()
def payment_term(project_end_date: datetime) -> str:
    """
    コンビニ/Pay-easy決済の支払い期限計算
    
    :param project_end_date: プロジェクト終了日
    :return: 支払い期限日
    """
    today = datetime.today()
    if project_end_date.date() == today.date():
        return None
    add_days = min(7, (project_end_date.date() - today.date()).days)
    payment_term_ = date.today() + timedelta(days=add_days - 1)
    weekday = ('(月)', '(火)', '(水)', '(木)', '(金)', '(土)', '(日)')
    return payment_term_.strftime('%Y年%m月%d日' + weekday[payment_term_.weekday()])


@app.template_filter()
def grouped_number(number: int) -> str:
    """
    数値をカンマ区切りにする
    :param number: 数値
    :return: カンマ区切りの数値
    """
    return "{:0,}".format(number)


@app.template_filter()
def format_profile(profile: str) -> str:
    """
    プロフィールの表示を整形する
    :param profile: プロフィール文字列
    :return: 整形済みプロフィール文字列
    """
    profile = profile.strip()
    profile = re.sub(r'[\r\n ]+', ' ', profile)
    return profile
