import secrets
from urllib.parse import urlencode
from fastapi import Request
from starlette.templating import Jinja2Templates
from jinja2 import pass_context

from db_models import AnonymousUser
from utils import GENDERS, ACTIVITY_LEVELS, FITNESS_GOALS, EXERCISE_LOCATIONS

templates = Jinja2Templates(directory="templates")

ENDPOINT_MAP = {
    'main.home': '/',
    'main.guest_form': '/try',
    'main.guest_predict': '/try/predict',
    'main.fitness_form': '/form',
    'main.predict': '/predict',
    'main.register': '/register',
    'main.login': '/login',
    'main.logout': '/logout',
    'main.dashboard': '/dashboard',
    'main.delete_account': '/delete-account',
    'main.reset_password': '/reset-password',
    'main.google_login': '/auth/google',
    'main.google_callback': '/auth/google/callback',
    'home': '/',
    'guest_form': '/try',
    'guest_predict': '/try/predict',
    'fitness_form': '/form',
    'predict': '/predict',
    'register': '/register',
    'login': '/login',
    'logout': '/logout',
    'dashboard': '/dashboard',
    'delete_account': '/delete-account',
    'reset_password': '/reset-password',
    'google_login': '/auth/google',
    'google_callback': '/auth/google/callback',
}


@pass_context
def jinja_url_for(context, endpoint: str, **values):
    request = context.get('request')
    if endpoint == 'static':
        filename = values.get('filename') or values.get('path') or ''
        return f"/static/{filename.lstrip('/')}"

    base_path = ENDPOINT_MAP.get(endpoint, endpoint if endpoint.startswith('/') else f"/{endpoint}")

    token = values.pop('token', None)
    if token:
        base_path = f"{base_path.rstrip('/')}/{token}"

    _external = values.pop('_external', False)

    query_params = {k: v for k, v in values.items() if v is not None and v != ''}
    url = base_path
    if query_params:
        url = f"{url}?{urlencode(query_params)}"

    if _external and request:
        url = f"{request.base_url.scheme}://{request.base_url.netloc}{url}"

    return url


@pass_context
def jinja_get_flashed_messages(context, with_categories: bool = False):
    request = context.get('request')
    if not request or not hasattr(request, 'session'):
        return []
    flashes = request.session.pop('_flashes', [])
    if with_categories:
        return flashes
    return [msg for _, msg in flashes]


@pass_context
def jinja_csrf_token(context):
    request = context.get('request')
    if not request or not hasattr(request, 'session'):
        return ''
    token = request.session.get('_csrf_token')
    if not token:
        token = secrets.token_hex(32)
        request.session['_csrf_token'] = token
    return token


# Register Jinja globals
templates.env.globals['url_for'] = jinja_url_for
templates.env.globals['get_flashed_messages'] = jinja_get_flashed_messages
templates.env.globals['csrf_token'] = jinja_csrf_token
templates.env.globals['GENDERS'] = GENDERS
templates.env.globals['ACTIVITY_LEVELS'] = ACTIVITY_LEVELS
templates.env.globals['FITNESS_GOALS'] = FITNESS_GOALS
templates.env.globals['EXERCISE_LOCATIONS'] = EXERCISE_LOCATIONS


def flash(request: Request, message: str, category: str = 'info'):
    if '_flashes' not in request.session:
        request.session['_flashes'] = []
    request.session['_flashes'].append((category, message))


def render_template(request: Request, template_name: str, context: dict = None, status_code: int = 200):
    if context is None:
        context = {}
    context['request'] = request

    current_user = context.get('current_user')
    if not current_user:
        current_user = getattr(request.state, 'user', None) or AnonymousUser()
        context['current_user'] = current_user

    if 'user' not in context:
        context['user'] = current_user

    return templates.TemplateResponse(request=request, name=template_name, context=context, status_code=status_code)
