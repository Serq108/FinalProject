from django.contrib.auth.tokens import PasswordResetTokenGenerator
#from django.utils import six
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

BASE_URL = 'http://localhost:8000'


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # return (six.text_type(user.id) + six.text_type(timestamp)) + six.text_type(user.is_active)
        return (user.id + timestamp) + user.is_active


token_generator = AccountActivationTokenGenerator()


def create_email_confirm_url(user_id, token):
    return '{}/auth/confirm_email/{}/{}'.format(
        BASE_URL,
        urlsafe_base64_encode(force_bytes(user_id)),
        token
    )
