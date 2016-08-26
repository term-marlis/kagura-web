import json
import urllib

import swagger_client as sw
from flask import jsonify, request, Blueprint, g, current_app, session
from flask_login import current_user
from swagger_client.rest import ApiException

from web.modules.form import CheckoutForm, DeleteForm

blueprint = Blueprint('api', __name__)

states = [
    ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'), ('05', '秋田県'),
    ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'), ('09', '栃木県'), ('10', '群馬県'),
    ('11', '埼玉県'), ('12', '千葉県'), ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'),
    ('16', '富山県'), ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'),
    ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'), ('25', '滋賀県'),
    ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'), ('29', '奈良県'), ('30', '和歌山県'),
    ('31', '鳥取県'), ('32', '島根県'), ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'),
    ('36', '徳島県'), ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'),
    ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'), ('45', '宮崎県'),
    ('46', '鹿児島県'), ('47', '沖縄県')
]


def join_name(last_name: str, first_name: str):
    return last_name.replace(' ', '') + ' ' + first_name.replace(' ', '')


def get_item_answers(project_id: int, item_id: int, form: dict):
    answers = []
    project_api = sw.ProjectApi(g.api)
    questions = project_api.projects_project_id_items_item_id_questions_get(
        project_id=project_id, item_id=item_id)
    for question in questions:
        key = 'answer_' + str(question.id)
        if key in form:
            answer = sw.Answer()
            answer.id = question.id
            answer.value = form[key]
            answers.append(answer)
    return answers


@blueprint.route('/checkout', methods=['POST'])
def api_checkout():
    if not current_user.is_authenticated:
        return jsonify({'code': '403', 'retryable': False, 'message': 'ログインし直してください。'})
    print(request.form)
    form = CheckoutForm(request.form)
    if form.validate_on_submit():
        print(form.data)
        checkout = sw.Checkout()
        checkout.payment_type = form.payment_type.data
        # 住所情報
        checkout.zip_code = form.shipping_zipcode.data.replace('-', '')
        checkout.pref = form.shipping_state.data
        checkout.town = form.shipping_town.data
        checkout.address = form.shipping_address.data
        checkout.building = form.shipping_building.data
        checkout.phone = form.shipping_phone.data.replace('-', '')
        checkout.full_name = join_name(form.shipping_last_name.data, form.shipping_first_name.data)
        if checkout.payment_type == 'credit':
            checkout.card_token = form.payment_credit_token.data
        if checkout.payment_type == 'cvs':
            checkout.cvs_code = form.payment_cvs_code.data
            checkout.customer_name = join_name(form.payment_cvs_last_name.data,
                                               form.payment_cvs_first_name.data)[:20]
            checkout.customer_kana = join_name(form.payment_cvs_last_name_kana.data,
                                               form.payment_cvs_first_name_kana.data)[:20]
            checkout.customer_tel_no = form.payment_cvs_tel_no.data.replace('-', '')
        if checkout.payment_type == 'payeasy':
            checkout.customer_name = join_name(form.payment_payeasy_last_name.data,
                                               form.payment_payeasy_first_name.data)[:20]
            checkout.customer_kana = join_name(form.payment_payeasy_last_name_kana.data,
                                               form.payment_payeasy_first_name_kana.data)[:20]
            checkout.customer_tel_no = form.payment_payeasy_tel_no.data.replace('-', '')
        project_id = form.project_id.data
        item_id = form.item_id.data
        checkout.answers = get_item_answers(project_id=project_id, item_id=item_id, form=request.form)
        print(checkout)
        try:
            project_api = sw.ProjectApi(g.api)
            result = project_api.projects_project_id_items_item_id_checkout_post(project_id=project_id,
                                                                                 item_id=item_id,
                                                                                 checkout=checkout)
            print(result)
            return jsonify(result.to_dict())
        except ApiException as ex:
            current_app.logger.error(ex)
            print(ex.status)
            print(ex.reason)
            return jsonify(json.loads(ex.body))
    print(form.errors)
    print(form.data)
    return jsonify({'code': '403', 'retryable': False, 'message': '想定外のエラーが発生しました。しばらくしてからやり直してください。'})


@blueprint.route('/zipcode')
def api_zipcode():
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    zipcode = request.args.get('zipcode')
    if zipcode:
        url = 'http://zipcloud.ibsnet.co.jp/api/search?zipcode=%s' % zipcode
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode("utf-8"))
        if result['message']:
            return jsonify({'status': 'ng', 'message': 'invalid zipcode.'})
        elif result['results'] and len(result['results']) > 0:
            item = result['results'][0]
            code = 13
            for code, name in states:
                if name == item['address1']:
                    break
            address = '%s %s' % (item['address2'], item['address3'],)
            return jsonify({'status': 'ok', 'code': int(code), 'address': address})
        else:
            return jsonify({'status': 'ng', 'message': 'address is not found.'})
    else:
        return jsonify({'status': 'ng', 'message': '`zipcode` is required.'})


@blueprint.route('/questions/<int:project_id>/<int:item_id>/<int:question_id>')
def api_questions(project_id, item_id, question_id):
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    if current_user.is_user:
        return jsonify({'login': False})
    project_api = sw.ProjectApi(g.api)
    question = project_api.projects_project_id_items_item_id_questions_question_id_get(project_id=project_id,
                                                                                       item_id=item_id,
                                                                                       question_id=question_id)
    return jsonify(question.to_dict())


@blueprint.route('/validators/<int:project_id>/<int:item_id>')
def api_validators(project_id, item_id):
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    project_api = sw.ProjectApi(g.api)
    questions = project_api.projects_project_id_items_item_id_questions_get(project_id=project_id,
                                                                            item_id=item_id)
    fields = {}
    for question in questions:
        rules = []
        if question.is_required:
            # 必須チェック
            rules.append({'type': 'empty', 'prompt': '「%s」を入力してください' % question.description})
        if question.type == 'number':
            if question.is_required and question.format:
                # 数値：範囲チェック
                rules.append({
                    'type': 'integer[%s]' % question.format.replace('-', ',').replace(',', '..'),
                    'prompt': '「%s」は%sの範囲で入力してください'
                              % (question.description, question.format.replace('-', 'から'),)})
            else:
                rules.append({'type': 'maxLength[10]',
                              'prompt': '「%s」は10桁以内で入力してください' % question.description})
        fields['answer_' + str(question.id)] = {
            'identifier': 'answer_' + str(question.id),
            'rules': rules
        }
    return jsonify({
        'on': 'blur',
        'keyboardShortcuts': False,
        'fields': fields
    })


@blueprint.route('/my/address')
def api_my_address():
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    my_api = sw.MyApi(g.api)
    addresses = my_api.my_addresses_get()
    for address in addresses:  # "fullname"を"first_name"と"last_name"に分割する
        address_data = address.to_dict()
        splitted_fullname = address.full_name.split(' ', 1)
        address_data['last_name'] = splitted_fullname[0] if len(splitted_fullname) > 1 else address.full_name
        address_data['first_name'] = splitted_fullname[1] if len(splitted_fullname) > 1 else None
        return jsonify({'login': True, 'address': address_data})
    return jsonify({'login': True})


@blueprint.route('/my/card')
def api_my_card():
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    my_api = sw.MyApi(g.api)
    cards = my_api.my_cards_get()
    for card in cards:
        return jsonify({'login': True, 'card': card.to_dict()})
    return jsonify({'login': True})


@blueprint.route('/email/<string:category>')
def api_email(category):
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    mail_magazine = sw.MailMagazine()
    mail_magazine.category = category
    mail_magazine.checked = True
    my_api = sw.MyApi(g.api)
    mail = my_api.my_email_put(mail_magazine=mail_magazine)
    return jsonify({'login': True, category: mail.to_dict()})


@blueprint.route('/favorite/<int:creator_id>')
def api_favorite(creator_id: int):
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    my_api = sw.MyApi(g.api)
    if 'action' in request.args:
        favorite = sw.Favorite()
        favorite.creator_id = creator_id
        favorite.checked = (request.args['action'] == 'on')
        favorite = my_api.my_favorites_put(favorite=favorite)
        return jsonify({'login': True, 'favorite': favorite.to_dict()})
    else:
        favorite = my_api.my_favorites_creator_id_get(creator_id=creator_id)
        if favorite.creator_id:
            return jsonify({'login': True, 'favorite': favorite.to_dict()})
    return jsonify({'login': True})


@blueprint.route('/notify/undelivery')
def api_close_undelivery_notify():
    if not current_user.is_authenticated:
        return jsonify({'count': -1})
    notify_count = 0
    if 'notify_count' in session:
        notify_count = session['notify_count']
    session['notify_count'] = notify_count + 1
    return jsonify({'count': current_user.email_status_notify_count})


@blueprint.route('/delete', methods=['POST'])
def api_delete():
    if not current_user.is_authenticated:
        return jsonify({'login': False})
    if current_user.is_user:
        return jsonify({'login': False})
    form = DeleteForm(request.form)
    if form.validate_on_submit():
        project_api = sw.ProjectApi(g.api)
        if form.question_id.data:
            project_api.projects_project_id_items_item_id_questions_question_id_delete(project_id=form.id.data,
                                                                                       item_id=form.item_id.data,
                                                                                       question_id=form.question_id.data)
            return jsonify({'msg': 'delete project item question.'})
        if form.item_id.data:
            project_api.projects_project_id_items_item_id_delete(project_id=form.id.data, item_id=form.item_id.data)
            return jsonify({'msg': 'delete project item.'})
        if form.faq_id.data:
            project_api.projects_project_id_faqs_faq_id_delete(project_id=form.id.data, faq_id=form.faq_id.data)
            return jsonify({'msg': 'delete project faq.'})
        if form.report_id.data:
            project_api.projects_project_id_reports_report_id_delete(project_id=form.id.data,
                                                                     report_id=form.report_id.data)
            return jsonify({'msg': 'delete project report.'})
        if form.id.data:
            project_api.projects_project_id_delete(project_id=form.id.data)
            return jsonify({'msg': 'delete project.'})
    return jsonify({'msg': 'does not delete.'})
