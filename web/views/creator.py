import swagger_client as sw
from flask import Blueprint, render_template, request, url_for, flash, current_app, g, jsonify, session, Response, abort
from flask_login import current_user, login_required, logout_user
from swagger_client.rest import ApiException

from web.modules import utils, converter
from web.modules.form import CreatorLoginForm, SignupForm, ProjectBasicForm, ProjectItemForm, ProjectDetailForm, \
    ProjectReportForm, ImageForm, MediaForm, ProjectItemQuestionForm, ProjectFaqForm, DeleteForm, PasswordMailForm, \
    PasswordResetForm
from web.modules.utils import check_device
from web.views.common import login_user_, logout_user_, redirect_

blueprint = Blueprint('creator', __name__, template_folder='creator_templates')


@blueprint.before_request
def before_creator_view():
    if 'CREATOR_IP_LIST' in current_app.config:
        if 'X-Forwarded-For' not in request.headers:
            abort(404)
        elif request.headers['X-Forwarded-For'] \
                not in current_app.config.get('CREATOR_IP_LIST'):
            abort(404)
    if request.path in ['/_creator/signup', '/_creator/login', '/_creator/password']:
        # 認証不要
        return
    if not current_user.is_anonymous and current_user.is_creator:
        # クリエイターでログイン済
        return
    return redirect_(url_for('creator.login'))


@blueprint.route('/')
@login_required
def home():
    """クリエイター: ホーム画面"""
    project_api = sw.ProjectApi(api_client=g.api)
    projects = project_api.projects_get()
    return render_template('creator_home.html', projects=projects)


@blueprint.route('/project/new', methods=['GET', 'POST'])
@login_required
def project_new():
    """プロジェクト: 新規作成"""
    basic_form = ProjectBasicForm(request.form)
    if basic_form.validate_on_submit():
        project_ = converter.project_form_to_api_project(basic_form)
        project_api = sw.ProjectApi(g.api)
        project_ = project_api.projects_post(project_)
        flash('プロジェクトを登録しました', category='info')
        return redirect_(url_for('creator.project_edit_basic', project_id=project_.id))
    utils.flash_errors(basic_form)
    return render_template('creator_project_new.html', basic_form=basic_form)


@blueprint.route('/project/<int:project_id>')
@login_required
def project(project_id: int):
    """プロジェクト: 詳細"""
    project_api = sw.ProjectApi(api_client=g.api)
    try:
        project_ = project_api.projects_project_id_get(project_id=project_id)
        reports_ = project_api.projects_project_id_reports_get(project_id=project_id)
        return render_template('creator_project.html', project=project_, reports=reports_, form=DeleteForm())
    except:
        return redirect_(url_for('creator.home'))


@blueprint.route('/project/<int:project_id>/edit/basic', methods=['GET', 'POST'])
@login_required
def project_edit_basic(project_id):
    """プロジェクト(基本情報): 編集"""
    basic_form = ProjectBasicForm(request.form)
    project_api = sw.ProjectApi(g.api)
    if 'image' in request.files and request.files['image'].filename:
        image = request.files['image']
        if image.content_length < 1048577:  # 画像は1MB制限
            file_path = utils.upload_file_to_s3(prefix='project', file=image)
            project_ = sw.Project()
            project_.image = file_path
            project_api.projects_project_id_put(project_id=project_id, project=project_)
        else:
            flash('画像は1MB以下にしてください', category='error')
    elif basic_form.validate_on_submit():
        project_ = converter.project_form_to_api_project(basic_form)
        project_api.projects_project_id_put(project_id=project_id, project=project_)
        flash('プロジェクト(基本情報)を更新しました', category='info')
    utils.flash_errors(basic_form)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    basic_form = converter.api_project_to_project_form(project_)
    return render_template('creator_project_edit_basic.html', title="Edit Project",
                           project=project_, basic_form=basic_form)


@blueprint.route('/project/<int:project_id>/edit/item', methods=['GET', 'POST'])
@login_required
def project_edit_item(project_id):
    """プロジェクト(アイテム): 編集"""
    item_id = int(request.args.get('item_id')) if 'item_id' in request.args else None
    item_form = ProjectItemForm(request.form)
    project_api = sw.ProjectApi(g.api)
    if 'image' in request.files and request.files['image'].filename:
        image = request.files['image']
        if image.content_length < 1048577:  # 画像は1MB制限
            file_path = utils.upload_file_to_s3(prefix='item', file=image)
            item = sw.ProjectItem()
            item.image = file_path
            project_api.projects_project_id_items_item_id_put(project_id=project_id, item_id=item_id, project_item=item)
        else:
            flash('画像は1MB以下にしてください', category='error')
    elif item_form.validate_on_submit():
        item = converter.item_form_to_api_item(item_form)
        if item_id:
            project_api.projects_project_id_items_item_id_put(project_id=project_id, item_id=item_id, project_item=item)
            flash('アイテムを更新しました', category='info')
        else:
            project_api.projects_project_id_items_post(project_id=project_id, project_item=item)
            flash('アイテムを追加しました', category='info')
        return redirect_(url_for('creator.project_edit_item', project_id=project_id))
    utils.flash_errors(item_form)
    project_api = sw.ProjectApi(g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    if not project_.id:
        return abort(404)
    items = project_api.projects_project_id_items_get(project_id=project_id)
    item_form = ProjectItemForm()
    questions_ = None
    if item_id:
        item_ = project_api.projects_project_id_items_item_id_get(project_id=project_id, item_id=item_id)
        item_form = converter.api_item_to_project_item_form(item_)
        questions_ = project_api.projects_project_id_items_item_id_questions_get(project_id=project_id, item_id=item_id)
    return render_template('creator_project_edit_item.html', title="Edit Project", item_id=item_id,
                           project=project_, items=items, item_form=item_form,
                           questions=questions_, question_form=ProjectItemQuestionForm(), form=DeleteForm())


@blueprint.route('/project/<int:project_id>/edit/item/<int:item_id>', methods=['POST'])
@login_required
def project_edit_item_question(project_id, item_id):
    question_form = ProjectItemQuestionForm(request.form)
    if question_form.validate_on_submit():
        project_api = sw.ProjectApi(g.api)
        question = converter.item_question_form_to_api_item_question(question_form=question_form)
        if question.id:
            project_api.projects_project_id_items_item_id_questions_question_id_put(project_id=project_id,
                                                                                    item_id=item_id,
                                                                                    question_id=question.id,
                                                                                    project_item_question=question)
            flash('アイテム質問を更新しました', category='info')
        else:
            project_api.projects_project_id_items_item_id_questions_post(project_id=project_id, item_id=item_id,
                                                                         project_item_question=question)
            flash('アイテム質問を追加しました', category='info')
    utils.flash_errors(question_form)
    return redirect_(url_for('creator.project_edit_item', project_id=project_id, item_id=item_id))


@blueprint.route('/project/<int:project_id>/edit/detail', methods=['GET', 'POST'])
@login_required
def project_edit_detail(project_id):
    """プロジェクト(詳細): 編集"""
    detail_form = ProjectDetailForm(request.form)
    project_api = sw.ProjectApi(g.api)
    if detail_form.validate_on_submit():
        project_ = converter.project_detail_form_to_api_project(detail_form=detail_form)
        project_api.projects_project_id_put(project_id=project_id, project=project_)
        flash('プロジェクト(詳細情報)を更新しました', category='info')
    utils.flash_errors(detail_form)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    detail_form = converter.api_project_to_project_detail_form(project_)
    return render_template('creator_project_edit_detail.html', title="Edit Project",
                           project=project_, detail_form=detail_form,
                           image_form=ImageForm(), media_form=MediaForm())


@blueprint.route('/project/<int:project_id>/edit/faq', methods=['GET', 'POST'])
@login_required
def project_edit_faq(project_id):
    """プロジェクト(FAQ): 編集"""
    faq_id = int(request.args.get('faq_id')) if 'faq_id' in request.args else None
    faq_form = ProjectFaqForm(request.form)
    project_api = sw.ProjectApi(g.api)
    if faq_form.validate_on_submit():
        faq = converter.project_faq_form_to_api_project_faq(faq_form=faq_form)
        if faq_id:
            project_api.projects_project_id_faqs_faq_id_put(project_id=project_id, faq_id=faq_id, project_faq=faq)
            flash('FAQを更新しました', category='info')
        else:
            project_api.projects_project_id_faqs_post(project_id=project_id, project_faq=faq)
            flash('FAQを追加しました', category='info')
        return redirect_(url_for('creator.project_edit_faq', project_id=project_id))
    utils.flash_errors(faq_form)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    project_faqs = project_api.projects_project_id_faqs_get(project_id=project_id)
    if faq_id:
        faq = project_api.projects_project_id_faqs_faq_id_get(project_id=project_id, faq_id=faq_id)
        faq_form = converter.api_project_faq_to_project_faq_form(faq)
    return render_template('creator_project_edit_faq.html', title="Edit Project",
                           project=project_, project_faqs=project_faqs,
                           faq_id=faq_id, faq_form=faq_form, form=DeleteForm())


@blueprint.route('/project/<int:project_id>/review')
@login_required
def project_review(project_id):
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = sw.Project()
    project_.is_approval = 0  # (承認ステータス) 3:未申請 -> 0:未承認 -> 1:承認済み
    project_api.projects_project_id_put(project_id=project_id, project=project_)
    flash('プロジェクトの審査を開始しました。', category='info')
    return redirect_(url_for('creator.project', project_id=project_id))


@blueprint.route('/project/<int:project_id>/report', methods=['GET', 'POST'])
@login_required
def project_report(project_id):
    """プロジェクト: 活動報告"""
    report_id = int(request.args.get('report_id')) if 'report_id' in request.args else None
    report_form = ProjectReportForm(request.form)
    if report_form.validate_on_submit():
        project_api = sw.ProjectApi(g.api)
        report_ = converter.report_form_to_api_report(report_form)
        if report_id:
            project_api.projects_project_id_reports_report_id_put(project_id=project_id, report_id=report_id,
                                                                  project_report=report_)
            flash('レポートを更新しました', category='info')
        else:
            project_api.projects_project_id_reports_post(project_id=project_id, project_report=report_)
            flash('レポートを追加しました', category='info')
        return redirect_(url_for('creator.project', project_id=project_id))
    utils.flash_errors(report_form)
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    if report_id:
        report = project_api.projects_project_id_reports_report_id_get(project_id=project_id, report_id=report_id)
        report_form = converter.api_report_to_report_form(report)
    return render_template('creator_project_report.html', project=project_, form=report_form, report_id=report_id,
                           form_image=ImageForm(), form_media=MediaForm())


@blueprint.route('/supports/<int:project_id>')
@login_required
def supports(project_id):
    """サポート: 一覧"""
    project_api = sw.ProjectApi(api_client=g.api)
    project_ = project_api.projects_project_id_get(project_id=project_id)
    return render_template('creator_supports.html', project=project_)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """クリエイターのログイン画面"""
    if current_user.is_authenticated:
        logout_user_()
        return redirect_(url_for('creator.login'))
    form = CreatorLoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            auth_api = sw.AuthApi(api_client=g.api)
            auth = sw.Authenticate()
            auth.key = form.email.data
            auth.secret = form.password.data
            auth.device = check_device(user_agent=request.user_agent)
            try:
                token = auth_api.authenticate_post(authenticate=auth)
                current_app.logger.info("success login!")
                login_user_(token.access_token)
                return redirect_(url_for('creator.home'))
            except ApiException as ex:
                current_app.logger.warning('creator login: %s', ex)
                flash('メールアドレスまたはパスワードが不正です', category='error')
        else:
            flash('メールアドレスまたはパスワードが不正です', category='error')
    return render_template('creator_login.html', form=form)


@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    """クリエイターの登録画面"""
    if current_user.is_authenticated:
        logout_user()
        if 'token' in session:
            session.pop('token')
        return redirect_(url_for('creator.signup'))
    form = SignupForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = sw.User()
            user.nickname = form.username.data
            user.email = form.email.data
            user.password = form.password.data
            try:
                creator_api = sw.CreatorApi(api_client=g.api)
                creator_api.creators_post(user=user)
                return redirect_(url_for('creator.login'))
            except ApiException as ex:
                flash('登録済みのメールアドレスです', category='error')
                current_app.logger.warning(ex)
    return render_template('creator_signup.html', form=form)


@blueprint.route('/password', methods=['GET', 'POST'])
def password_request():
    """クリエイター: パスワードリセット要求"""
    mail_form = PasswordMailForm(request.form)
    if mail_form.validate_on_submit():
        creator_api = sw.CreatorApi(g.api)
        pwd_request = sw.PasswordRequest()
        pwd_request.email = mail_form.email.data
        pwd_request.reset_url = current_app.config.get('WEB_HOST') + url_for('creator.password_reset')
        try:
            result = creator_api.creators_password_post(password_request=pwd_request)
            current_app.logger.info(result)
            return render_template('creator_password_thanks.html')
        except ApiException as ex:
            flash('無効なメールアドレスです', category='error')
            current_app.logger.info(ex)
    return render_template('creator_password.html', form=PasswordMailForm())


@blueprint.route('/password/reset', methods=['GET', 'POST'])
def password_reset():
    reset_form = PasswordResetForm(request.form)
    creator_api = sw.CreatorApi(g.api)
    if reset_form.validate_on_submit():
        pwd_reset = sw.PasswordReset()
        pwd_reset.reset_token = reset_form.token.data
        pwd_reset.password = reset_form.password.data
        try:
            result = creator_api.creators_password_put(password_reset=pwd_reset)
            current_app.logger.info(result)
            return redirect_(url_for('creator.login'))
        except ApiException as ex:
            flash('パスワード再設定URLが有効期限切れです', category='error')
            current_app.logger.info(ex)
    if 'token' in request.args:
        token = request.args['token']
        try:
            result = creator_api.creators_password_get(reset_token=token)
            current_app.logger.info(result)
            reset_form.token.data = token
            return render_template('creator_password_reset.html', form=reset_form)
        except ApiException as ex:
            flash('パスワード再設定URLが有効期限切れです', category='error')
            current_app.logger.info(ex)
    return redirect_(url_for('creator.password_request'))


@blueprint.route('/upload/file', methods=['POST'])
@login_required
def upload_file():
    form = MediaForm(request.form)
    if ('file' in request.files) and (not form.csrf_token.errors):
        import mimetypes
        file = request.files['file']
        content_type = mimetypes.guess_type(file.filename)[0]
        # 画像は1MB制限 / 動画は5GB制限
        if (content_type.startswith('image') and file.content_length < 1048577) or (
                    content_type.startswith('video') and file.content_length < 1073741824 * 5):
            file_path = utils.upload_file_to_s3(prefix='media', file=file)
            return jsonify({
                'url': current_app.config.get('CDN_BASE_URL') + 'media/' + file_path,
                'name': file.filename
            })
    return jsonify({})


@blueprint.route('/logout')
def logout() -> Response:
    """ログアウト"""
    logout_user_()
    return redirect_(url_for('creator.login'))
