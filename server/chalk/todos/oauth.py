"""
Module to provide Google OAuth integrations
"""
import json
import os

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import google_auth_oauthlib.flow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

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

    # TODO use offline access to get a refresh token
    # Needed for integration test auth workflows,
    # printed below in _get_authorized_session
    # authorization_url, _ = flow.authorization_url(access_type='offline')
    authorization_url, _ = flow.authorization_url()
    return authorization_url


class OAuthBackend(BaseBackend):
    """
    OAuth backend for Django user authentication
    """

    def authenticate(self, request, **kwargs):
        user_model = get_user_model()
        token = kwargs['token']

        if 'state' in request.GET:
            session = _get_authorized_session(token, request.GET['state'])
        elif 'ci_refresh' in request.GET:
            with open(CLIENT_SECRETS_FILE, 'r') as client_secrets_file:
                client_secrets_data = client_secrets_file.read()
            client_secrets_obj = json.loads(client_secrets_data)["web"]

            session = AuthorizedSession(
                Credentials(
                    None,
                    refresh_token=token,
                    token_uri=client_secrets_obj['token_uri'],
                    client_id=client_secrets_obj['client_id'],
                    client_secret=client_secrets_obj['client_secret'],
                ))
        else:
            session = AuthorizedSession(Credentials(token))

        email = _get_email(session)
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


def _get_email(session):
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    return profile_info['email']


def _get_authorized_session(token, state):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    flow.fetch_token(code=token)
    # print(flow.credentials.refresh_token)

    session = flow.authorized_session()
    return session
