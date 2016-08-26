import logging
import os

import boto3
from redis import Redis

DEBUG = False
SECRET_KEY = 'development key'
SESSION_REDIS = Redis(host=os.environ['REDIS_HOST'], port=6379)
PREFERRED_URL_SCHEME = 'https'

WEB_HOST = 'http://192.168.99.100:5000'
API_HOST = '%s:9000' % os.environ['API_HOST']

LOG_LEVEL = logging.INFO
LOG_PATH = 'logs/app.log'

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
