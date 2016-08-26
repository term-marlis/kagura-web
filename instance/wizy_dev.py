"""
AWS検証環境用設定ファイル
"""
import logging

import boto3
from redis import Redis

DEBUG = False
SECRET_KEY = b'\xdf5\x85 P\x06\x82=\xbb\xf8\xb7\xdc\xa8\xe7\x1b\xaa\x8d!QD\xdf\x1c\xf2\x15'
SESSION_REDIS = Redis(host='cache-dev.peach.develop.recochoku.net', port=6379)
SESSION_COOKIE_SECURE = True
PREFERRED_URL_SCHEME = 'https'

WEB_HOST = 'https://peach.dev.recochoku.net'
API_HOST = 'https://peach-api.dev.recochoku.net'

CREATOR_IP_LIST = ['113.36.47.98', '122.218.209.226']

LOG_LEVEL = logging.INFO
LOG_PATH = '/var/log/recochoku/F-standard/P-3m/K-disable/web.log'

CLUB_RECOCHOKU_LOGIN = 'https://club.dev.recochoku.net/web/auth/login/login/'
CLUB_RECOCHOKU_SIGNUP = 'https://club.dev.recochoku.net/web/regist/selection/'
CLUB_RECOCHOKU_SILENT_RETURN = 'https://club.dev.recochoku.net/web/auth/silentReturn/'
CLUB_RECOCHOKU_EDIT_PASS = 'https://club.dev.recochoku.net/web/myaccount/pwdchange/'
CLUB_RECOCHOKU_EDIT_PROF = 'https://club.dev.recochoku.net/web/myaccount/profile/'
CLUB_RECOCHOKU_EDIT_MAIL = 'https://club.dev.recochoku.net/web/myaccount/mailchange/'

CDN_BASE_URL = 'https://resource.lap.recochoku.jp/e11/'
S3_BUCKET_NAME = 'peach-resource-dev'
AWS_S3_CLIENT = boto3.client('s3', 'ap-northeast-1')

GMO_SHOP_ID = 'tshop00022553'
GMO_SCRIPT_URL = 'https://pt01.mul-pay.jp/ext/js/token.js'
FAQ_SITE_URL= 'https://stg18.dga.jp'
