
import json
import os
from .support import dotdict
from .upload_video import upload_video
from .get_credentials import get_credentials
from google.oauth2.credentials import Credentials
from .get_category_number import get_category_number
from colorama import init, Fore
from pathlib import Path


def upload_from_options(options):
    """
    secrets_path: |
        ...

    cresentials_path: |
        credentials

    videos:
        -
            title:  video title
            file:  path
            description: sdf
            category: 22
            privacy: private
            tags:
                - shit
                - holy
    """
    options = dotdict(**options)

    credentials = None
    secrets = None

    if 'credentials' in options:
        credentials = Credentials.from_authorized_user_info(json.loads(options.credentials))

    elif 'credentials_path' in options and Path(options.credentials_path).exists():
        credentials = Credentials.from_authorized_user_file(options.credentials_path)

    elif Path('./credentials.json').exists():
        credentials = Credentials.from_authorized_user_file(options.credentials_path)

    elif 'secrets' in options:
        secrets = json.loads(options.secrets)

    elif 'secrets_path' in options and Path(options.secrets_path).exists():
        file = open(options.secrets_path, 'r')
        secrets = json.loads(file.read())
        file.close()

    if not credentials and secrets:
        credentials = get_credentials(secrets)
        save_credentials(credentials, options.credentials_path or "./credentials.json")
    elif not credentials and not secrets:
        raise Exception('neither secrets or credentials')

    for video_options in options.videos:

        if 'category' in video_options:
            video_options['category'] = get_category_number(video_options['category'])

        try:
            upload_video(
                credentials,
                **video_options
            )

        except Exception as e:
            init(autoreset=True)
            print(Fore.RED + str(e))

    return dump_credentials(credentials)



def save_credentials(creds, credentials_path):

    creds_data = dump_credentials(creds)

    del creds_data['token']

    secrets_path = os.path.dirname(credentials_path)
    if not os.path.isdir(secrets_path):
        os.makedirs(secrets_path)

    with open(credentials_path, 'w') as outfile:
        json.dump(creds_data, outfile)


def dump_credentials(creds):
    creds_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    return creds_data
