import swagger_client as sw


class LoginUser:
    def __init__(self, profile: sw.Profile):
        self.id = profile.user_id
        self.member_id = profile.member_id
        self.username = profile.nickname
        self.email = profile.email
        self.email_status = profile.email_status
        self.email_status_notify_count = 0  # アンデリ通知表示回数
        self.is_active = True
        self.is_authenticated = (profile.user_id is not None)
        self.is_anonymous = (profile.user_id is None)
        self.is_user = (profile.type == 'user')
        self.is_creator = (profile.type == 'creator')
        self.is_admin = (profile.type == 'admin')

    def get_id(self):
        """ログイン用"""
        return str(self.id)

    def __repr__(self):
        return 'LoginUser %s %s' % (self.id, self.username)
