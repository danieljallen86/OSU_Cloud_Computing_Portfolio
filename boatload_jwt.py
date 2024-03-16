# from google.cloud import datastore
# from flask import Flask, request, session, make_response, render_template, redirect
import constants
import requests
import string
import random


# app = Flask(__name__)

# client = datastore.Client()


def get_access_code_url(state):
    api_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    response_type = 'code'
    redirect_uri = f'{constants.app_url}/owners'
    scope = 'https://www.googleapis.com/auth/userinfo.profile'

    return f'{api_url}?response_type={response_type}&'\
        f'client_id={constants.client_id}&redirect_uri={redirect_uri}&'\
        f'scope={scope}&state={state}'


def request_token(access_code):
    api_url = 'https://www.googleapis.com/oauth2/v4/token'
    g_data = {
        'code': access_code,
        'client_id': constants.client_id,
        'client_secret': constants.client_secret,
        'redirect_uri': f'{constants.app_url}/owners', 
        'grant_type': 'authorization_code',
    }

    resp = requests.post(api_url, data=g_data)
    return resp.json()['id_token']


def make_state():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    state_dig = string.digits

    state = ''
    state += ''.join(random.choice(lowercase) for _ in range(26))
    state += ''.join(random.choice(uppercase) for _ in range(26))
    state += ''.join(random.choice(state_dig) for _ in range(10))

    return ''.join(random.sample(state, len(state)))


def validate_jwt(token):
    tok_info = requests.get(
        f'https://oauth2.googleapis.com/tokeninfo?id_token={token}').json()

    if 'sub' in tok_info.keys():
        return tok_info
