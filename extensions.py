import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()

oauth = OAuth()
google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

if google_client_id and google_client_secret:
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
