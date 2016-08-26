"""
WIZY本番環境用設定ファイル
"""
import logging

import boto3
from redis import Redis

DEBUG = False
SECRET_KEY = b'\x8a\xd2\xf8\xb8\xd41\xaf\x97r\xeew\xc6b\xcd\xa4[X\xa5\xdf\xd6{g*\xfb'
SESSION_REDIS = Redis(host='cache-pro.peach.product.recochoku.net', port=6379)
SESSION_COOKIE_SECURE = True
PREFERRED_URL_SCHEME = 'https'

WEB_HOST = 'https://wizy.jp'
API_HOST = 'https://api.wizy.jp'

CREATOR_IP_LIST = ['113.36.47.98', '122.218.209.226']

LOG_LEVEL = logging.INFO
LOG_PATH = '/var/log/recochoku/F-standard/P-3m/K-disable/web.log'

CLUB_RECOCHOKU_LOGIN = 'https://club.recochoku.jp/web/auth/login/login/'
CLUB_RECOCHOKU_SIGNUP = 'https://club.recochoku.jp/web/regist/selection/'
CLUB_RECOCHOKU_SILENT_RETURN = 'https://club.recochoku.jp/web/auth/silentReturn/'
CLUB_RECOCHOKU_EDIT_PASS = 'https://club.recochoku.jp/web/myaccount/pwdchange/'
CLUB_RECOCHOKU_EDIT_PROF = 'https://club.recochoku.jp/web/myaccount/profile/'
CLUB_RECOCHOKU_EDIT_MAIL = 'https://club.recochoku.jp/web/myaccount/mailchange/'

CDN_BASE_URL = 'https://resource.lap.recochoku.jp/e13/'
S3_BUCKET_NAME = 'peach-resource-pro'
AWS_S3_CLIENT = boto3.client('s3', 'ap-northeast-1')

GMO_SHOP_ID = '9100925033557'
GMO_SCRIPT_URL = 'https://p01.mul-pay.jp/ext/js/token.js'
GOOGLE_TAG_MANAGER = 'GTM-M7H5T3'
GOOGLE_ANALYTICS = 'UA-81007330-1'
FAQ_SITE_URL = 'https://help.wizy.jp'
