"""
Module to provide Google OAuth integrations
"""
import os

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import google_auth_oauthlib.flow

CLIENT_SECRETS_FILE = "/mnt/oauth_web_client_secret.json"
REDIRECT_URI = f'http://{os.environ["DOMAIN"]}/api/todos/auth_callback/'
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email']


def get_authorization_url():
    """
    Create an authorization URL to redirect a user to for OAuth login
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    authorization_url, _ = flow.authorization_url()
    return authorization_url


class OAuthBackend(BaseBackend):
    """
    OAuth backend for Django user authentication
    """

    def authenticate(self, request, **kwargs):
        user_model = get_user_model()
        email = _get_email(kwargs['token'], request.GET['state'])
        if email:
            try:
                user = user_model.objects.get(username=email)
            except user_model.DoesNotExist:
                user = user_model(username=email, email=email)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None


def _get_email(token, state):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    flow.fetch_token(code=token)

    session = flow.authorized_session()
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    return profile_info['email']
