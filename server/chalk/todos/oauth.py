"""
Module to provide Google OAuth integrations
"""
import json
import logging
import os

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import google_auth_oauthlib.flow
from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials

CLIENT_SECRETS_FILE = "/mnt/oauth_web_client_secret.json"
REDIRECT_URI = f'https://{os.environ["DOMAIN"]}/api/todos/auth_callback/'
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email']
logger = logging.getLogger(__name__)


def get_authorization_url(host):
    """
    Create an authorization URL to redirect a user to for OAuth login
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = _get_redirect_uri(host)

    # NOTE using offline access to get a refresh token
    # is needed for integration test auth workflows.
    # It's printed below in _get_authorized_session
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
        session = None

        if 'state' in request.GET:
            session = _get_authorized_session(token, request.GET['state'],
                                              request.get_host())
        elif 'ci_refresh' in request.GET:
            client_secrets_obj = _get_clients_secret_obj()
            session = AuthorizedSession(
                Credentials(
                    None,
                    refresh_token=token,
                    token_uri=client_secrets_obj['token_uri'],
                    client_id=client_secrets_obj['client_id'],
                    client_secret=client_secrets_obj['client_secret'],
                ))

        if session is not None:
            email = _get_email_from_session(session)
        else:
            email = _get_email_from_id_token(token)

        if email:
            try:
                user = user_model.objects.get(username=email)
            except user_model.DoesNotExist:
                permitted_users = os.getenv('PERMITTED_USERS', '').split(',')
                if email not in permitted_users:
                    return None
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


def _get_clients_secret_obj():
    with open(CLIENT_SECRETS_FILE, 'r',
              encoding='UTF-8') as client_secrets_file:
        client_secrets_data = client_secrets_file.read()
    return json.loads(client_secrets_data)["web"]


def _get_email_from_id_token(token):
    try:
        client_secrets_obj = _get_clients_secret_obj()
        id_info = id_token.verify_oauth2_token(token, Request(),
                                               client_secrets_obj['client_id'])
        return id_info['email']
    except ValueError:
        logger.exception('Error getting the email from the the ID token')
    return None


def _get_email_from_session(session):
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    return profile_info['email']


def _get_authorized_session(token, state, host):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = _get_redirect_uri(host)

    flow.fetch_token(code=token)
    # NOTE printed for setup of integration test auth workflows
    # print(flow.credentials.refresh_token)

    session = flow.authorized_session()
    return session


def _get_redirect_uri(host):
    if not settings.DEBUG:
        return REDIRECT_URI

    if host == 'localhost:8080':
        return REDIRECT_URI.replace(f'https://{os.environ["DOMAIN"]}',
                                    'http://localhost:8080')
    return REDIRECT_URI
