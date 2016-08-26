"""
web-testの設定

dockerでローカルに環境を構築した場合はこちらの設定を利用します
"""
import logging
import os

import boto3
from redis import Redis

DEBUG = True
DESIGN = True
SECRET_KEY = 'development key'
SESSION_REDIS = Redis(host=os.environ['REDIS_HOST'], port=6379)
PREFERRED_URL_SCHEME = 'https'

WEB_HOST = 'http://localhost:5000'
API_HOST = '%s:9000' % os.environ['API_HOST']

LOG_LEVEL = logging.INFO
LOG_PATH = 'logs/app.log'

CLUB_RECOCHOKU_LOGIN = 'http://localhost:5000/debug/login'
CLUB_RECOCHOKU_SIGNUP = 'http://localhost:5000/debug/login'
CLUB_RECOCHOKU_SILENT_RETURN = 'https://club.dev.recochoku.net/web/auth/silentReturn/'
CLUB_RECOCHOKU_EDIT_PASS = 'https://club.dev.recochoku.net/web/myaccount/pwdchange/'
CLUB_RECOCHOKU_EDIT_PROF = 'https://club.dev.recochoku.net/web/myaccount/profile/'
CLUB_RECOCHOKU_EDIT_MAIL = 'https://club.dev.recochoku.net/web/myaccount/mailchange/'

CDN_BASE_URL = 'https://resource.lap.recochoku.jp/e11/'
S3_BUCKET_NAME = 'peach-resource-dev'

AWS_S3_CLIENT = boto3.client('s3', 'ap-northeast-1',
                             aws_access_key_id='AKIAJ62RMH767HWIS4XQ',
                             aws_secret_access_key='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')

GMO_SHOP_ID = 'tshop00022553'
GMO_SCRIPT_URL = 'https://pt01.mul-pay.jp/ext/js/token.js'
FAQ_SITE_URL= 'https://stg18.dga.jp'
