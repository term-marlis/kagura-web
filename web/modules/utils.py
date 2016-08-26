import base64
import mimetypes
import os
import pathlib
import struct
import uuid
from datetime import timedelta, datetime

import swagger_client as sw
from PIL import Image
from boto3.s3.transfer import S3Transfer
from flask import current_app, g, flash
from werkzeug.useragents import UserAgent


def upload_profile_image_to_tmp(file):
    extension = pathlib.Path(file.filename).suffix
    file_name = '%s%s' % (uuid.uuid4(), extension,)
    file_path = '%s%s' % (current_app.root_path + '/static/img/tmp/', file_name)
    try:
        file.save(file_path)
        img = Image.open(file_path)
        x, y = img.size
        if x and y:
            return file_name
        os.remove(file_path)
        return None
    except Exception as ex:
        os.remove(file_path)
        current_app.logger.error('failed to uplad profile image: %s', ex)


def profile_tmp_image_is_not_exists(src_file_name: str):
    src_file_path = '%s%s' % (current_app.root_path + '/static/img/tmp/', src_file_name)
    return not os.path.isfile(src_file_path)


def delete_profile_tmp_image(src_file_name: str):
    src_file_path = '%s%s' % (current_app.root_path + '/static/img/tmp/', src_file_name)
    if os.path.isfile(src_file_path):
        os.remove(src_file_path)


def upload_profile_image_to_s3(src_file_name: str, crop_size: tuple):
    src_file_path = '%s%s' % (current_app.root_path + '/static/img/tmp/', src_file_name)
    img = Image.open(src_file_path, 'r')
    cropped_img = img.crop(crop_size)
    cropped_img.thumbnail((200, 200), Image.ANTIALIAS)
    extension = pathlib.Path(src_file_name).suffix
    file_name = '%s%s' % (uuid.uuid4(), extension,)
    file_path = '%s%s' % (current_app.config.get('TMP_FILE_FOLDER'), file_name)
    if extension in ('jpg', 'jpeg', 'JPG', 'JPEG'):
        cropped_img.save(file_path, 'JPEG', quality=100, optimize=True)
    else:
        cropped_img.save(file_path, 'PNG', quality=100, optimize=True)
    file_s3_key = '%s/%s' % ('profile', file_name)
    uploader = S3Transfer(current_app.config.get('AWS_S3_CLIENT'))
    bucket = current_app.config.get('S3_BUCKET_NAME')
    content_type = mimetypes.guess_type(file_path)[0]
    uploader.upload_file(filename=file_path, bucket=bucket, key=file_s3_key,
                         extra_args={'ContentType': content_type})
    os.remove(src_file_path)
    os.remove(file_path)
    return file_name


def upload_file_to_s3(prefix, file):
    """
    ファイルアップロード
    :param prefix: 接頭辞
        common: CSS/JavaScriptなど
        profile: プロフィール画像
        project: プロジェクトメイン画像
        media: 詳細/レポート(Wysiwygの画像)
        item: アイテムの画像
    :param file: アップロードするファイル
    :return: ファイル名(実際のURLは接頭辞がつく)
    """
    if prefix.startswith('common'):
        file_name = file.filename
    else:
        extension = pathlib.Path(file.filename).suffix
        file_name = '%s%s' % (uuid.uuid4(), extension,)
    file_path = '%s%s' % (current_app.config.get('TMP_FILE_FOLDER'), file_name)
    file.save(file_path)
    file_s3_key = '%s/%s' % (prefix, file_name)
    uploader = S3Transfer(current_app.config.get('AWS_S3_CLIENT'))
    bucket = current_app.config.get('S3_BUCKET_NAME')
    content_type = mimetypes.guess_type(file_path)[0]
    uploader.upload_file(filename=file_path, bucket=bucket, key=file_s3_key,
                         extra_args={'ContentType': content_type})
    os.remove(file_path)
    return file_name


def check_device(user_agent: UserAgent) -> str:
    """デバイス種別判定

    :param user_agent: UserAgent
    """
    if not user_agent:
        return 'Others'
    if user_agent.platform == 'android':
        return 'Android'
    if user_agent.platform in ('ipad', 'iphone'):
        return 'iOS'
    if user_agent.platform in ('macos', 'windows', 'linux'):
        return 'PC'
    return 'Others'


def check_trid(cookies) -> str:
    try:
        if 'trid' in cookies:
            return ''.join(str('%08x' % x) for x in struct.unpack('<4L', base64.b64decode(cookies['trid']))).upper()
    except Exception as e:
        current_app.logger.error(e)


def user_support_project_ids():
    """
    ログイン中のユーザのサポートしているプロジェクト一覧を取得します
    サポーターの判定などに利用できます。
    """
    my_api = sw.MyApi(api_client=g.api)
    supports = my_api.my_supports_get()
    return set([support.project_id for support in supports])


def search_next_report(reports, report_id: int) -> (sw.ProjectReport, int, int):
    """
    レポート一覧から前後のレポートを取得する

    :param reports: レポート一覧
    :param report_id: 表示するレポートID
    :return: (表示する記事, 新しい記事, 過去の記事)
    """
    selected, next_report, previous_report = None, None, None
    for index, report in enumerate(reports):  # 選択中の記事に対して 過去の記事 と 新しい記事 を設定
        if report_id == report.id:
            selected = report
            next_report = reports[index - 1] if (index > 0) else None
            previous_report = reports[index + 1] if (index + 1 != len(reports)) else None
    return selected, next_report, previous_report


def get_project_reports(project_id: int) -> (list, bool):
    """
    レポートの一覧を取得する。更新のある記事かどうかの判定も一緒に行う。

    :param project_id: プロジェクトID
    :return: レポート一覧
    """
    project_api = sw.ProjectApi(api_client=g.api)
    reports = project_api.projects_project_id_reports_get(project_id=project_id)
    has_new_report = False
    public_reports = []
    for index, report in enumerate(reports):  # １週間以内の場合はNEWを表示
        if report.accessible == 'private':
            continue
        if report.update_date + timedelta(days=7) > datetime.today():
            report.is_new, has_new_report = True, True
        public_reports.append(report)
    return public_reports, has_new_report


def get_project_items(project: sw.Project) -> list:
    """
    アイテムの一覧を取得する。サポート可能かどうかの判定も一緒に行う。
    :param project: プロジェクト情報
    :return: アイテム一覧
    """
    today = datetime.today()
    my_api = sw.MyApi(api_client=g.api)
    supports = my_api.my_supports_get()
    project_api = sw.ProjectApi(api_client=g.api)
    items = project_api.projects_project_id_items_get(project_id=project.id)
    for item in items:
        if project.public_status in (1, 3, 4):  # 1:公開前,2:公開中(募集終了),3:非公開
            item.error_message = '募集期間外'
        elif today < project.start_time or project.end_time < today:
            item.error_message = '募集期間外'
        elif -1 < item.limit <= item.expected_supports:
            item.error_message = '在庫切れ'
        elif -1 < item.limit_user <= len([support for support in supports if support.item_id == item.id]):
            item.error_message = '購入制限超え'
    return items


def project_status_text(project: sw.Project):
    """
    プロジェクトステータスの文字列を取得する
    :param project: プロジェクト
    :return: ステータス文字列
    """
    if project.public_status == 1:
        return '公開前'
    if project.public_status == 2:
        return '実施中'
    if project.public_status == 3:
        if project.type in (1, 3):  # 実施確約/プレオーダー型
            return '終了'
        elif project.type == 2:  # チャレンジ型
            if project.target_amount <= project.current_amount:
                return '達成'
            else:
                return '未達成'
    if project.public_status == 4:
        return '非公開'


def flash_errors(form):
    """Formのエラーをflash領域に表示する"""
    for field, errors in form.errors.items():
        for error in errors:
            # getattr(form, field).label.text
            flash(error, category='error')
