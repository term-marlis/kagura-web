from datetime import datetime, timedelta, time

from colour import Color
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, IntegerField, PasswordField, SubmitField, \
    SelectField, TextAreaField, BooleanField, HiddenField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
from wtforms_components import DateField, TimeField, ColorField

states = [
    (1, '北海道'), (2, '青森県'), (3, '岩手県'), (4, '宮城県'), (5, '秋田県'),
    (6, '山形県'), (7, '福島県'), (8, '茨城県'), (9, '栃木県'), (10, '群馬県'),
    (11, '埼玉県'), (12, '千葉県'), (13, '東京都'), (14, '神奈川県'), (15, '新潟県'),
    (16, '富山県'), (17, '石川県'), (18, '福井県'), (19, '山梨県'), (20, '長野県'),
    (21, '岐阜県'), (22, '静岡県'), (23, '愛知県'), (24, '三重県'), (25, '滋賀県'),
    (26, '京都府'), (27, '大阪府'), (28, '兵庫県'), (29, '奈良県'), (30, '和歌山県'),
    (31, '鳥取県'), (32, '島根県'), (33, '岡山県'), (34, '広島県'), (35, '山口県'),
    (36, '徳島県'), (37, '香川県'), (38, '愛媛県'), (39, '高知県'), (40, '福岡県'),
    (41, '佐賀県'), (42, '長崎県'), (43, '熊本県'), (44, '大分県'), (45, '宮崎県'),
    (46, '鹿児島県'), ('47', '沖縄県')
]
cvs_code = [
    ('', '選択してください'),
    ('00001', 'ローソン'), ('00002', 'ファミリーマート'), ('00003', 'サンクス'), ('00004', 'サークルＫ'),
    ('00005', 'ミニストップ'), ('00006', 'デイリーヤマザキ'), ('00008', 'セイコーマート'), ('00009', 'スリーエフ')
]
today = datetime.today()
years = [('', '年')]
years.extend([(str(x), str(x) + '年') for x in range(2016, today.year + 21)])
months = [
    ('', '月'),
    ('1', '1月'), ('2', '2月'), ('3', '3月'), ('4', '4月'), ('5', '5月'), ('6', '6月'),
    ('7', '7月'), ('8', '8月'), ('9', '9月'), ('10', '10月'), ('11', '11月'), ('12', '12月'),
]


class CheckoutForm(Form):
    """購入フォーム"""
    project_id = IntegerField('Project ID', validators=[DataRequired()])
    item_id = IntegerField('Item ID', validators=[DataRequired()])
    """配達ありの場合は必須"""
    shipping_state = SelectField('都道府県', choices=states, coerce=int, default=13)
    shipping_zipcode = StringField('郵便番号', validators=[])
    shipping_fullname = StringField('氏名', validators=[])
    shipping_last_name = StringField('氏名(姓)', validators=[])
    shipping_first_name = StringField('氏名(名)', validators=[])
    shipping_town = StringField('市区町村', validators=[])
    shipping_address = StringField('番地', validators=[])
    shipping_building = StringField('建物名', validators=[])
    shipping_phone = StringField('電話番号', validators=[])
    """支払方法"""
    payment_type = StringField('支払方法', validators=[DataRequired()])
    """支払方法(credit)の場合は必須"""
    payment_credit_token = StringField('クレジットカードトークン', validators=[])
    """支払方法(payeasy)の場合は必須"""
    payment_payeasy_last_name = StringField('氏名(姓)', validators=[])
    payment_payeasy_first_name = StringField('氏名(名)', validators=[])
    payment_payeasy_last_name_kana = StringField('フリガナ(姓)', validators=[])
    payment_payeasy_first_name_kana = StringField('フリガナ(名)', validators=[])
    payment_payeasy_tel_no = StringField('電話番号', validators=[])
    """支払方法(cvs)の場合は必須"""
    payment_cvs_code = SelectField('コンビニ会社コード', choices=cvs_code, coerce=str, default='')
    payment_cvs_last_name = StringField('氏名(姓)', validators=[])
    payment_cvs_first_name = StringField('氏名(名)', validators=[])
    payment_cvs_last_name_kana = StringField('フリガナ(姓)', validators=[])
    payment_cvs_first_name_kana = StringField('フリガナ(名)', validators=[])
    payment_cvs_tel_no = StringField('電話番号', validators=[])
    """クレジットカード有効期限"""
    payment_credit_exp_month = SelectField('有効期限(月)', choices=months)
    payment_credit_exp_year = SelectField('有効期限(年)', choices=years)


class ProfileBasicForm(Form):
    """プロフィール編集(基本情報)"""
    nickname = StringField('ニックネーム',
                           validators=[DataRequired(message='ニックネームを入力してください')])
    profile = TextAreaField('プロフィール',
                            validators=[DataRequired(message='プロフィールを入力してください')])
    basic_submit = SubmitField('保存')


class MailMagazineForm(Form):
    """メルマガ設定"""
    news = BooleanField('ニュースレター')
    project = BooleanField('プロジェクトからのお知らせ')
    favorite = BooleanField('お気に入りのクリエイター')
    mail_submit = SubmitField('保存')


class CreatorProfileForm(Form):
    """クリエイターメール変更フォーム"""
    email = StringField('メールアドレス', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Length(min=1, max=200, message='メールアドレスは200文字以下で入力してください')
    ])
    link = URLField('リンク', validators=[
        Optional(),
        Length(min=1, max=500, message='WebサイトURLは500文字以下で入力してください')
    ])
    facebook = StringField('Facebook', validators=[
        Optional(),
        Length(min=5, max=50, message='Facebookアカウントは5~50文字で入力してください')
    ])
    twitter = StringField('Twitter', validators=[
        Optional(),
        Length(min=1, max=15, message='Twitterアカウントは1~15文字で入力してください')
    ])
    creator_submit = SubmitField('保存')


class CreatorPasswordForm(Form):
    """クリエイターパスワード変更フォーム"""
    password = PasswordField('パスワード', validators=[
        DataRequired(message='パスワードを入力してください'),
        Length(min=1, max=100, message='パスワードは100文字以下で入力してください')
    ])
    password_confirm = PasswordField('パスワード確認', validators=[
        DataRequired(message='パスワード確認を入力してください'),
        Length(min=1, max=100, message='パスワードは100文字以下で入力してください')
    ])
    password_submit = SubmitField('保存')


class CreatorLoginForm(Form):
    """ログイン"""
    email = StringField('Email', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Email(message='メールアドレスの形式で入力してください'),
        Length(min=1, max=200, message='メールアドレスは200文字以下で入力してください')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='パスワードを入力してください'),
        Length(min=1, max=100, message='パスワードは100文字以下で入力してください')
    ])
    submit = SubmitField('Login')


class SignupForm(Form):
    """クリエイター登録"""
    username = StringField('Username', validators=[
        DataRequired(message='ユーザー名を入力してください'),
        Length(min=1, max=200, message='ユーザー名は200文字以下で入力してください')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Length(min=1, max=200, message='メールアドレスは200文字以下で入力してください')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='パスワードを入力してください'),
        Length(min=1, max=100, message='パスワードは100文字以下で入力してください')
    ])
    password_confirm = PasswordField('Password', validators=[
        DataRequired(message='パスワード確認を入力してください'),
        Length(min=1, max=100, message='パスワード確認は100文字以下で入力してください')
    ])
    submit = SubmitField('Signup')


class PasswordMailForm(Form):
    """クリエイターパスワードリセット(メール送信)"""
    email = StringField('Email', validators=[
        DataRequired(message='メールアドレスを入力してください'),
        Email(message='メールアドレスの形式で入力してください'),
        Length(min=1, max=200, message='メールアドレスは200文字以下で入力してください')
    ])
    submit = SubmitField('Send')


class PasswordResetForm(Form):
    """クリエイターパスワードリセット(パスワード送信)"""
    password = PasswordField('Password', validators=[
        DataRequired(message='パスワードを入力してください'),
        Length(min=1, max=100, message='パスワードは100文字以下で入力してください')
    ])
    password_confirm = PasswordField('Password', validators=[
        DataRequired(message='パスワード確認を入力してください'),
        Length(min=1, max=100, message='パスワード確認は100文字以下で入力してください')
    ])
    token = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Reset')


class ProjectBasicForm(Form):
    """プロジェクト: 基本情報"""
    title = StringField('タイトル', validators=[DataRequired('タイトルを入力してください')])
    summary = TextAreaField('概要', validators=[DataRequired('概要を入力してください')])
    type = SelectField('タイプ', validators=[DataRequired()], coerce=int,
                       choices=[(1, '実施確約型'), (2, 'チャレンジ型'), (3, 'プレオーダー型'), ])
    target_amount = IntegerField('目標金額', default=1000000,
                                 validators=[
                                     DataRequired('目標金額を入力してください'),
                                     NumberRange(min=1, max=999999999,
                                                 message='目標金額は1〜999,999,999円で設定してください')
                                 ])
    open_amount = BooleanField('表示する', validators=[], default=True)
    start_date = DateField('開始日', validators=[], default=(datetime.today() + timedelta(days=7)).date())
    start_time = TimeField('開始時刻', validators=[], default=time(22, 0, 0, 0))
    end_date = DateField('終了日', validators=[], default=(datetime.today() + timedelta(days=87)).date())
    end_time = TimeField('終了時刻', validators=[], default=time(22, 0, 0, 0))
    main_color = SelectField('メインカラー', validators=[], coerce=str, choices=[('white', '白'), ('black', '黒'), ])
    accent_color = ColorField('アクセントカラー', validators=[], default=Color('#c5ac69'))
    image = FileField('画像', validators=[])
    submit = SubmitField('保存')


class ProjectItemForm(Form):
    """プロジェクト: アイテム"""
    name = StringField('名称', validators=[DataRequired(message='アイテム名称を入力してください')])
    price = IntegerField('価格(税込)', validators=[
        DataRequired(message='価格を入力してください'),
        NumberRange(min=1, message='価格は1円以上で設定してください')
    ], default=1000)
    shipping = BooleanField('配送あり', default=True)
    description = TextAreaField('内容', validators=[DataRequired(message='アイテム内容を入力してください')])
    limit = StringField('制限個数(全体)', validators=[], default=None)
    limit_user = StringField('制限個数(1人)', validators=[], default=None)
    deliver_date = DateField('お届け予定日', validators=[], default=datetime.today().date() + timedelta(days=100))
    image = FileField('画像', validators=[])
    submit = SubmitField('保存')


class ProjectItemQuestionForm(Form):
    """プロジェクト: アイテム質問"""
    question_id = HiddenField('ID', validators=[])
    description = StringField('質問内容', validators=[DataRequired()])
    required = BooleanField('必須項目', default=True)
    type = SelectField('回答種別', validators=[DataRequired()], default='text',
                       choices=[('text', 'テキスト'), ('number', '数値'), ('select', '選択'), ])
    format = StringField('回答書式', validators=[])
    submit = SubmitField('保存')


class ProjectDetailForm(Form):
    """プロジェクト: 詳細"""
    detail = TextAreaField('プロジェクト詳細', validators=[])
    note = TextAreaField('注意事項欄', validators=[])
    submit = SubmitField('保存')


class ProjectFaqForm(Form):
    """プロジェクト: FAQ"""
    question = StringField('質問項目', validators=[DataRequired(message='質問項目を入力してください')])
    answer = TextAreaField('回答内容', validators=[DataRequired(message='回答内容を入力してください')])
    submit = SubmitField('保存')


class ProjectReportForm(Form):
    """プロジェクト: 活動報告"""
    title = StringField('タイトル', validators=[
        DataRequired(message='タイトルを入力してください')
    ])
    report = TextAreaField('活動報告', validators=[DataRequired()])
    accessible = SelectField('公開範囲', validators=[DataRequired()], default='text',
                             choices=[('private', '非公開'), ('supporter', 'サポーター限定公開'), ('all', '全体に公開'), ])
    notification = BooleanField('ファンにメールで通知する')
    submit = SubmitField('保存')


class ImageForm(Form):
    """画像アップロード"""
    image = FileField('Report Image', validators=[FileRequired()])


class MediaForm(Form):
    """音源/動画アップロード"""
    media = FileField('Report Media', validators=[FileRequired()])


class DeleteForm(Form):
    """削除用"""
    id = StringField()
    report_id = StringField()
    item_id = StringField()
    question_id = StringField()
    faq_id = StringField()
