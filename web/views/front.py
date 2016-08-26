import urllib

import swagger_client as sw
from flask import redirect, url_for, session, current_app, Blueprint, g, Response, abort
from flask import request, render_template, flash, render_template_string
from flask_login import current_user, login_required
from swagger_client.rest import ApiException
from datetime import datetime
from web.modules import utils
from web.modules.form import CheckoutForm, ImageForm, ProfileBasicForm, MailMagazineForm, CreatorPasswordForm, \
    CreatorProfileForm
from web.modules.utils import check_device, check_trid, get_project_reports, search_next_report, \
    user_support_project_ids, get_project_items, project_status_text
from web.views.common import login_user_, logout_user_, redirect_

blueprint = Blueprint('front', __name__, template_folder='front_templates')


@blueprint.before_request
def before_front_view():
    agree = request.cookies.get('agree')
    if agree:
        session['agree'] = True


@blueprint.route('/')
def home() -> Response:
    """トップページ"""
    project_api = sw.ProjectApi(api_client=g.api)
    popular_projects = project_api.projects_get(popular=True)
    pickup_projects = project_api.projects_get(pickup=True)
    pickup_project = None
    for project_ in pickup_projects:
        pickup_project = project_
    return render_template('index.html', top_project=pickup_project, projects=popular_projects)


@blueprint.route('/projects')
@blueprint.route('/projects/')
def projects() -> Response:
    """プロジェクト一覧ページ"""
    project_api = sw.ProjectApi(api_client=g.api)
    projects = project_api.projects_get()
    return render_template('projects.html', projects=projects)


@blueprint.route('/project/<int:project_id>')
@blueprint.route('/project/<int:project_id>/')
def project(project_id: int) -> Response:
    """
    プロジェクト詳細

    :param project_id: プロジェクトID
    """
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    if not project_.id:
        return abort(404)
    items = get_project_items(project=project_)
    faqs = project_api.projects_project_id_faqs_get(project_id=project_id)
    reports, has_new_report = get_project_reports(project_id=project_id)
    is_supporter = project_id in user_support_project_ids()
    creator_api = sw.CreatorApi(g.api)
    creator = creator_api.creators_user_id_get(user_id=project_.user_id)
    return render_template('project.html', project=project_, items=items, faqs=faqs, reports=reports,
                           creator=creator, has_new_report=has_new_report, is_supporter=is_supporter)


@blueprint.route('/project/<int:project_id>/reports')
@blueprint.route('/project/<int:project_id>/reports/')
def project_reports(project_id: int) -> Response:
    """
    プロジェクト レポート一覧

    :param project_id: プロジェクトID
    """
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    if not project_.id:
        return abort(404)
    reports, has_new_report = get_project_reports(project_id=project_id)
    is_supporter = project_id in user_support_project_ids()
    creator_api = sw.CreatorApi(g.api)
    creator = creator_api.creators_user_id_get(user_id=project_.user_id)
    return render_template('project_reports.html', project=project_, reports=reports,
                           creator=creator, is_supporter=is_supporter)


@blueprint.route('/project/<int:project_id>/report/<int:report_id>')
@blueprint.route('/project/<int:project_id>/report/<int:report_id>/')
def project_report(project_id: int, report_id: int) -> Response:
    """
    プロジェクト レポート

    :param project_id: プロジェクトID
    :param report_id: レポートID
    """
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    if not project_.id:
        return abort(404)
    reports, has_new_report = get_project_reports(project_id=project_id)
    is_supporter = project_id in user_support_project_ids()
    selected, next_report, previous_report = search_next_report(reports=reports, report_id=report_id)
    if not selected:
        return abort(404)
    creator_api = sw.CreatorApi(g.api)
    creator = creator_api.creators_user_id_get(user_id=project_.user_id)
    return render_template('project_report.html', project=project_, report=selected, creator=creator,
                           previous_report=previous_report, next_report=next_report, is_supporter=is_supporter)


@blueprint.route('/checkout')
@blueprint.route('/checkout/')
def checkout() -> Response:
    """アイテム購入"""
    project_id = request.args.get('project')
    item_id = request.args.get('item')
    if not project_id:
        return redirect_(url_for('front.home'))
    if not item_id:
        return redirect_(url_for('front.project', project_id=project_id))
    if current_user.is_authenticated:
        project_api = sw.ProjectApi(api_client=g.api)
        project_ = project_api.projects_project_id_get(project_id=project_id)
        if not project_.id:  # 指定したIDのプロジェクトが存在しない
            return redirect_(url_for('front.home'))
        items = get_project_items(project=project_)
        item = [item for item in items if item_id == str(item.id)]
        if not item:  # 指定したIDのアイテムが存在しない
            return redirect_(url_for('front.project', project_id=project_id))
        questions = project_api.projects_project_id_items_item_id_questions_get(project_id=project_id, item_id=item_id)
        creator_api = sw.CreatorApi(g.api)
        creator = creator_api.creators_user_id_get(user_id=project_.user_id)
        return render_template('checkout.html', project=project_, items=items, creator=creator,
                               questions=questions, item=item[0], form=CheckoutForm())
    else:
        return redirect_(url_for('front.login'))


@blueprint.route('/profile')
@blueprint.route('/profile/')
@blueprint.route('/profile/favorite')
@blueprint.route('/profile/favorite/')
@login_required
def profile_favorite() -> Response:
    """お気に入り"""
    my_api = sw.MyApi(api_client=g.api)
    profile_ = my_api.my_profile_get()
    favorites = my_api.my_favorites_get()
    for favorite in favorites:
        project_api = sw.ProjectApi(api_client=g.api)
        projects_ = project_api.projects_get(creator=favorite.creator_id)
        for project_ in projects_:
            favorite.project_id = project_.id
            favorite.project_title = project_.title
            favorite.project_image = project_.image
            favorite.project_summary = project_.summary
    return render_template('profile_favorite.html', profile=profile_, favorites=favorites)


@blueprint.route('/profile/support')
@blueprint.route('/profile/support/')
@login_required
def profile_support() -> Response:
    """プロフィール"""
    my_api = sw.MyApi(api_client=g.api)
    profile_ = my_api.my_profile_get()
    supports = my_api.my_supports_get()
    for support in supports:
        project_api = sw.ProjectApi(api_client=g.api)
        project_ = project_api.projects_project_id_get(project_id=support.project_id)
        if project_:
            support.project_title = project_.title
            support.project_image = project_.image
            support.project_status = project_.public_status
            support.project_status_text = project_status_text(project_)
            support.project_end_time = project_.end_time
        item_ = project_api.projects_project_id_items_item_id_get(project_id=support.project_id,
                                                                  item_id=support.item_id)
        if item_:
            support.item_name = item_.name
        if item_.shipping:  # 配送ありの場合はお届け先を表示
            shipping = my_api.my_shippings_support_id_get(support_id=support.support_id)
            if shipping.zipcode:
                from web.modules.form import states
                pref_name = [state[1] for state in states if state[0] == shipping.pref]
                if pref_name and len(pref_name) > 0:
                    shipping.pref_name = pref_name[0]
                zipcode = shipping.zipcode
                if shipping.zipcode and len(shipping.zipcode) == 7:
                    zipcode = shipping.zipcode[:3] + '-' + shipping.zipcode[3:]
                support.shipping_address = '%s %s %s %s %s' % (
                    zipcode, shipping.pref_name, shipping.town, shipping.address, shipping.building)
        if support.status == 1:  # 決済未完了の場合は支払い情報を表示
            order = my_api.my_orders_order_id_get(order_id=support.order_id)
            if order:
                if order.cust_id:
                    support.payment_code = order.cust_id + '-' + order.conf_no
                if order.receipt_no:
                    support.payment_code = order.receipt_no + '-' + order.conf_no
                    from web.modules.form import cvs_code
                    support.payment_cvs_name = [code[1] for code in cvs_code if str(code[0]) == order.cvs_code][0]
                support.payment_term = order.payment_term
    return render_template('profile_support.html', profile=profile_, supports=supports)


@blueprint.route('/profile/edit', methods=['GET', 'POST'])
@blueprint.route('/profile/edit/', methods=['GET', 'POST'])
@login_required
def profile_edit() -> Response:
    """プロフィール編集"""
    my_api = sw.MyApi(api_client=g.api)
    profile_ = my_api.my_profile_get()
    basic_form = ProfileBasicForm(request.form)
    mail_form = MailMagazineForm(request.form)
    creator_form = CreatorProfileForm(request.form)
    password_form = CreatorPasswordForm(request.form)
    if request.method == 'POST':
        if basic_form.basic_submit.data and basic_form.validate_on_submit():
            profile_.nickname = basic_form.nickname.data
            profile_.introduction = basic_form.profile.data
            my_api.my_profile_put(user=profile_)
            flash('プロフィールを更新しました', category='info')
        elif mail_form.mail_submit.data and mail_form.validate_on_submit():
            for category in ['news', 'project', 'favorite']:
                mail_magazine = sw.MailMagazine()
                mail_magazine.category = category
                mail_magazine.checked = mail_form[category].data
                my_api.my_email_put(mail_magazine=mail_magazine)
            flash('メルマガ設定を更新しました', category='info')
        elif creator_form.creator_submit.data and creator_form.validate_on_submit():
            profile_.email = creator_form.email.data
            profile_.facebook = creator_form.facebook.data
            profile_.twitter = creator_form.twitter.data
            profile_.link = creator_form.link.data
            try:
                my_api.my_profile_put(user=profile_)
                flash('クリエイター情報を更新しました', category='info')
            except ApiException as ex:
                current_app.logger.warning('creator profile error: %s', ex)
                flash('クリエイター情報の更新に失敗しました', category='error')
        elif password_form.password_submit.data and password_form.validate_on_submit():
            # TODO パスワードの更新
            print(password_form.data)
            flash('パスワードを更新しました', category='info')
        utils.flash_errors(basic_form)
        utils.flash_errors(mail_form)
        utils.flash_errors(creator_form)
        utils.flash_errors(password_form)
        return redirect_(url_for('front.profile_edit'))
    else:
        if 'profile_image' in session and utils.profile_tmp_image_is_not_exists(session['profile_image']):
            utils.delete_profile_tmp_image(session['profile_image'])
            session.pop('profile_image')
        profile_ = my_api.my_profile_get()
        basic_form.nickname.data = profile_.nickname
        basic_form.profile.data = profile_.introduction
        emails_ = my_api.my_email_get()
        for email in emails_:
            mail_form[email.category].data = email.checked
        creator_form.email.data = profile_.email
        creator_form.facebook.data = profile_.facebook
        creator_form.twitter.data = profile_.twitter
        creator_form.link.data = profile_.link
    return render_template('profile_edit.html', profile=profile_, image_form=ImageForm(),
                           basic_form=basic_form, mail_form=mail_form,
                           creator_form=creator_form, password_form=password_form)


@blueprint.route('/profile/image', methods=['POST'])
@login_required
def profile_image() -> Response:
    """プロフィール編集"""
    image_form = ImageForm(request.form)
    if image_form.csrf_token.errors:
        abort(401)
    if 'image' in request.files and request.files['image']:
        image = request.files['image']
        if image.content_length < 1048577:  # 画像は1MB制限
            file_name = utils.upload_profile_image_to_tmp(file=image)
            if file_name:
                session['profile_image'] = file_name
            else:
                flash('画像ファイルを選択してください', category='error')
        else:
            flash('アップロード可能な画像サイズは1MBまでです', category='error')
    elif 'profile_image' in session:
        if 'width' in request.form and 'height' in request.form \
                and 'x' in request.form and 'y' in request.form:
            crop_size = (int(request.form['x']), int(request.form['y']),
                         (int(request.form['x']) + int(request.form['width'])),
                         (int(request.form['y']) + int(request.form['height'])))
            file_path = utils.upload_profile_image_to_s3(src_file_name=session['profile_image'],
                                                         crop_size=crop_size)
            my_api = sw.MyApi(api_client=g.api)
            profile_ = my_api.my_profile_get()
            profile_.image = file_path
            my_api.my_profile_put(user=profile_)
            flash('画像をアップロードしました', category='info')
        else:
            utils.delete_profile_tmp_image(src_file_name=session['profile_image'])
        session.pop('profile_image')
    return redirect_(url_for('front.profile_edit'))


@blueprint.route('/profile/edit/<string:edit_type>')
@blueprint.route('/profile/edit/<string:edit_type>/')
def member_edit(edit_type: str) -> Response:
    """
    ユーザ情報変更(クラブレコチョク)

    :param edit_type: 変更種別
    """
    ok_url = urllib.parse.quote(current_app.config.get('WEB_HOST') + '/login?next=/profile/')
    param = '?service=wizy&devices_type=WEB&ok_url='
    silent_url = urllib.parse.quote(current_app.config.get('CLUB_RECOCHOKU_SILENT_RETURN') + param + ok_url)
    if edit_type == 'password':
        return redirect(current_app.config.get('CLUB_RECOCHOKU_EDIT_PASS') + param + silent_url)
    if edit_type == 'profile':
        return redirect(current_app.config.get('CLUB_RECOCHOKU_EDIT_PROF') + param + silent_url)
    if edit_type == 'mail':
        return redirect(current_app.config.get('CLUB_RECOCHOKU_EDIT_MAIL') + param + silent_url)
    return redirect_(url_for('front.profile_favorite'))


@blueprint.route('/login')
def login() -> Response:
    """クラブレコチョクからの戻りURL"""
    if 'enable_id' in request.args:
        user_agent = request.headers.get('User-Agent')
        current_app.logger.info('User-Agent: %s' % user_agent)
        auth = sw.Authenticate()
        auth.key = 'session_key'
        auth.secret = request.args['enable_id']
        auth.device = check_device(request.user_agent)
        auth.trid = check_trid(cookies=request.cookies)
        auth_api = sw.AuthApi(g.api)
        try:
            token = auth_api.authenticate_post(authenticate=auth)
            login_user_(access_token=token.access_token)
            if 'next' in request.args and 'logout' not in request.args['next']:
                if 'regist' in request.args:
                    return redirect_(request.args['next'] + '?regist=complete')
                return redirect_(request.args['next'])
            if 'regist' in request.args:
                return redirect_(url_for('front.home') + '?regist=complete')
            return redirect_(url_for('front.home'))
        except ApiException as ex:
            current_app.logger.warning('login error: %s', ex)
            flash('認証に失敗しました', category='error')
        return redirect_(url_for('front.home'))
    if current_user.is_authenticated:
        return redirect_(url_for('front.home'))
    """クラブレコチョクへ認証しに行く"""
    if request.referrer and request.referrer.startswith(current_app.config.get('WEB_HOST')):
        next_ = request.referrer.replace(current_app.config.get('WEB_HOST'), '')
        ok_url = urllib.parse.quote(current_app.config.get('WEB_HOST') + '/login?next=' + next_)
        ok_url_regist = urllib.parse.quote(current_app.config.get('WEB_HOST') + '/login?regist=complete?next=' + next_)
    else:
        ok_url = urllib.parse.quote(current_app.config.get('WEB_HOST') + '/login')
        ok_url_regist = urllib.parse.quote(current_app.config.get('WEB_HOST') + '/login?regist=complete')
    param = '?service=wizy&devices_type=WEB&ok_url='
    silent_url = urllib.parse.quote(current_app.config.get('CLUB_RECOCHOKU_SILENT_RETURN') + param + ok_url)
    silent_url_r = urllib.parse.quote(current_app.config.get('CLUB_RECOCHOKU_SILENT_RETURN') + param + ok_url_regist)
    session.clear()
    silent_params = param + silent_url + '&ok_url_regist=' + silent_url_r
    if 'signup' in request.args:
        response = redirect(current_app.config.get('CLUB_RECOCHOKU_SIGNUP') + silent_params)
    else:
        response = redirect(current_app.config.get('CLUB_RECOCHOKU_LOGIN') + silent_params)
    response.set_cookie('agree', value=str(datetime.now().timestamp()))
    return response


@blueprint.route('/logout')
def logout() -> Response:
    """ログアウト"""
    logout_user_()
    return render_template('plain.html', message='ログアウトしました')


"""
CSS動的生成
"""


@blueprint.route('/css/project/<int:project_id>')
def dynamic_css_project(project_id: int):
    redis = current_app.config.get('SESSION_REDIS')
    cache_key = 'dynamic_css_project_%s' % project_id
    if not redis.exists(cache_key):
        from colour import Color
        import math
        project_api = sw.ProjectApi(api_client=g.api)
        project = project_api.projects_project_id_get(project_id=project_id)
        if project.id:
            cc = Color(color=project.accent_color)
            accent_color_rgb = '%s, %s, %s' % (
                math.floor(cc.get_red() * 255), math.floor(cc.get_green() * 255), math.floor(cc.get_blue() * 255))
            cdn_base_url = current_app.config.get('CDN_BASE_URL')
            stylesheet_str = render_template('project.css.template', accent_color=project.accent_color,
                                             accent_color_rgb=accent_color_rgb, cdn_base_url=cdn_base_url)
            redis.set(cache_key, stylesheet_str, ex=60)
        else:
            abort(404)
    content = redis.get(cache_key)
    return Response(content, content_type='text/css')


"""
制作用カスタムページ
"""


@blueprint.route('/campaign')
@blueprint.route('/campaign/')
@blueprint.route('/campaign/<string:path>')
@blueprint.route('/campaign/<string:path>/')
def campaign_page(path: str = 'index') -> Response:
    return custom_page('campaign', path)


@blueprint.route('/info')
@blueprint.route('/info/')
@blueprint.route('/info/<string:path>')
@blueprint.route('/info/<string:path>/')
def info_page(path: str = 'index') -> Response:
    return custom_page('info', path)


@blueprint.route('/special')
@blueprint.route('/special/')
@blueprint.route('/special/<string:path>')
@blueprint.route('/special/<string:path>/')
def special_page(path: str = 'index') -> Response:
    return custom_page('special', path)


@blueprint.route('/about')
@blueprint.route('/about/')
@blueprint.route('/about/<string:path>')
@blueprint.route('/about/<string:path>/')
def about_page(path: str = 'index') -> Response:
    return custom_page('about', path)


def custom_page(prefix: str, path: str) -> Response:
    """カスタム画面(仮)
    制作側の要望でS3のバケットにページを置いたら反映できる仕組みがあると良い
    - その他: バナーの表示, info的なページもあると良いかも？ということです。
    # req = requests.get(url, stream=True)
    # return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])

    :param prefix: フォルダ
    :param path: ファイルパス
    """
    redis = current_app.config.get('SESSION_REDIS')
    if redis.exists(path):
        content_type = redis.get(path + '_')
        content = redis.get(path)
        return Response(content, content_type=content_type)
    # TODO common配下をローカルで確認する場合はこちらを使用する
    if current_app.config.get('DESIGN'):
        if '.' not in path:
            path += '.html'
        try:
            print(current_app.root_path + '/static/cdn/pages/%s/%s' % (prefix, path,))
            file = open(current_app.root_path + '/static/cdn/pages/%s/%s' % (prefix, path,))
            response = render_template_string(file.read(), message='%s/%s' % (prefix, path,))
            file.close()
            return response
        except:
            abort(404)
    # TODO common配下をCDNから取得する場合はこちらを使用する
    import requests
    if '.' not in path:
        path += '.html'
        url = 'http://%s.s3-website-ap-northeast-1.amazonaws.com/common/pages/%s/%s' \
              % (current_app.config.get('S3_BUCKET_NAME'), prefix, path,)
        req = requests.get(url)
        if req.status_code == 200:
            return render_template_string(req.content.decode('utf-8'), message='%s/%s' % (prefix, path,))
        abort(404)
    else:
        url = 'http://%s.s3-website-ap-northeast-1.amazonaws.com/common/pages/%s/%s' \
              % (current_app.config.get('S3_BUCKET_NAME'), prefix, path,)
        req = requests.get(url)
        content = req.content
        content_type = req.headers['content-type']
        redis.set(path + '_', content_type, ex=60)
        redis.set(path, content, ex=60)
        return Response(content, content_type=content_type)
