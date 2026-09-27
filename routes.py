import logging
import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from db_models import User, Result, UserProfile, AnonymousUser
from extensions import oauth
from auth import get_current_user, login_required, verify_csrf
from templates import render_template, flash
from utils import (validate_predict_form, build_notes, build_split, build_exercises,
                   run_prediction, check_training_bounds,
                   generate_reset_token, verify_reset_token)

logger = logging.getLogger("ai_fitness")
router = APIRouter()


# ── Home ──────────────────────────────────────────────────────────────────────
@router.get('/')
async def home(request: Request, current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/form', status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url='/try', status_code=status.HTTP_303_SEE_OTHER)


# ── Guest prediction (no login required) ─────────────────────────────────────
@router.get('/try')
async def guest_form(request: Request, current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/form', status_code=status.HTTP_303_SEE_OTHER)
    ref = request.query_params.get('ref', '')
    return render_template(request, 'guest_form.html', {'ref': ref})


@router.post('/try/predict')
async def guest_predict(request: Request):
    form = dict(await request.form())
    verify_csrf(request, form)

    data, error = validate_predict_form(form)
    if error:
        flash(request, f'Please fix the following: {error}', 'danger')
        return RedirectResponse(url='/try', status_code=status.HTTP_303_SEE_OTHER)

    model = request.app.state.model
    try:
        bf_pct = run_prediction(data, model)
    except Exception as e:
        logger.exception("Guest prediction failed: %s", e)
        flash(request, 'Prediction failed. Please check your inputs and try again.', 'danger')
        return RedirectResponse(url='/try', status_code=status.HTTP_303_SEE_OTHER)

    # Store in session so we can save it after sign-up
    request.session['guest_result'] = {**data, 'bf_pct': bf_pct}

    notes     = build_notes(data['goal'], bf_pct, data['gender'])
    split     = build_split(data['workouts'])
    exercises = build_exercises(split, data['exercise_location'])
    unusual_warnings = check_training_bounds(data)

    ref = form.get('ref', '')

    return render_template(
        request,
        'result.html',
        {
            'bf_pct': bf_pct,
            'gender': data['gender'],
            'age': data['age'],
            'height': data['height'],
            'weight': data['weight'],
            'split': split,
            'notes': notes,
            'exercises': exercises,
            'exercise_location': data['exercise_location'],
            'unusual_warnings': unusual_warnings,
            'is_guest': True,
            'ref': ref,
        }
    )


# ── Auth ──────────────────────────────────────────────────────────────────────
@router.get('/register')
async def register_page(request: Request, current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)
    ref = request.query_params.get('ref', '')
    return render_template(request, 'register.html', {'ref': ref})


@router.post('/register')
async def register(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)

    form = dict(await request.form())
    verify_csrf(request, form)

    name     = form.get('name', '').strip()
    email    = form.get('email', '').strip().lower()
    password = form.get('password', '').strip()
    ref_code = form.get('ref', '').strip()

    if not name or not email or not password:
        flash(request, 'All fields are required.', 'danger')
        return render_template(request, 'register.html', {'ref': ref_code})

    if db.query(User).filter(User.email == email).first():
        flash(request, 'Email already registered. Please login.', 'danger')
        return render_template(request, 'register.html', {'ref': ref_code})

    # Handle referral
    referrer = None
    if ref_code:
        referrer = db.query(User).filter(User.referral_code == ref_code).first()

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        referred_by=referrer.id if referrer else None,
    )
    db.add(user)

    if referrer:
        referrer.referral_count = (referrer.referral_count or 0) + 1

    db.commit()
    db.refresh(user)

    # Save any guest prediction that was done before sign-up
    _save_guest_result(request, user, db)

    request.session['user_id'] = user.id
    return RedirectResponse(url='/form', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/login')
async def login_page(request: Request, current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)
    return render_template(request, 'login.html')


@router.post('/login')
async def login(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.is_authenticated:
        return RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)

    form = dict(await request.form())
    verify_csrf(request, form)

    email    = form.get('email', '').strip().lower()
    password = form.get('password', '').strip()

    if not email or not password:
        flash(request, 'Email and password are required.', 'danger')
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.email == email).first()

    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        flash(request, 'Invalid email or password.', 'danger')
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    request.session['user_id'] = user.id
    _save_guest_result(request, user, db)

    dest = '/dashboard' if user.results else '/form'
    return RedirectResponse(url=dest, status_code=status.HTTP_303_SEE_OTHER)


# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get('/auth/google')
async def google_login(request: Request):
    ref = request.query_params.get('ref', '')
    request.session['oauth_ref'] = ref
    redirect_uri = str(request.url_for('google_callback'))
    if request.headers.get("x-forwarded-proto") == "https":
        redirect_uri = redirect_uri.replace("http://", "https://", 1)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get('userinfo') or await oauth.google.userinfo(request, token=token)
    except Exception as e:
        logger.exception("Google OAuth login failed: %s", e)
        flash(request, 'Google login failed. Please try again.', 'danger')
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    google_id = userinfo.get('sub')
    email     = userinfo.get('email', '').lower()
    name      = userinfo.get('name', email.split('@')[0])

    # Find or create user
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id   # link existing account
        else:
            ref_code = request.session.pop('oauth_ref', '')
            referrer = None
            if ref_code:
                referrer = db.query(User).filter(User.referral_code == ref_code).first()
            user = User(
                name=name, email=email,
                google_id=google_id,
                referred_by=referrer.id if referrer else None,
            )
            db.add(user)
            if referrer:
                referrer.referral_count = (referrer.referral_count or 0) + 1
        db.commit()
        db.refresh(user)

    request.session['user_id'] = user.id
    _save_guest_result(request, user, db)

    dest = '/dashboard' if user.results else '/form'
    return RedirectResponse(url=dest, status_code=status.HTTP_303_SEE_OTHER)


# ── Password Recovery ─────────────────────────────────────────────────────────
@router.get('/reset-password')
@router.get('/reset-password/{token}')
async def reset_password_get(request: Request, token: str = None):
    secret_key = request.app.state.secret_key
    effective_token = token or request.query_params.get('token', '').strip()

    if effective_token:
        email = verify_reset_token(effective_token, secret_key, max_age=1800)
        if not email:
            flash(request, 'The reset link is invalid or has expired (30-minute limit). Please request a new one.', 'danger')
            return RedirectResponse(url='/reset-password', status_code=status.HTTP_303_SEE_OTHER)
        return render_template(request, 'reset_password.html', {'token': effective_token, 'email': email})

    return render_template(request, 'reset_password.html', {'token': None})


@router.post('/reset-password')
@router.post('/reset-password/{token}')
async def reset_password_post(request: Request, db: Session = Depends(get_db), token: str = None):
    secret_key = request.app.state.secret_key
    form = dict(await request.form())
    verify_csrf(request, form)

    effective_token = token or request.query_params.get('token', '').strip() or form.get('token', '').strip()

    # Flow A: Token provided -> Validate token and update password
    if effective_token:
        email = verify_reset_token(effective_token, secret_key, max_age=1800)
        if not email:
            flash(request, 'The reset link is invalid or has expired (30-minute limit). Please request a new one.', 'danger')
            return RedirectResponse(url='/reset-password', status_code=status.HTTP_303_SEE_OTHER)

        new_password = form.get('password', '').strip()
        if not new_password:
            flash(request, 'Password cannot be empty.', 'danger')
            return render_template(request, 'reset_password.html', {'token': effective_token, 'email': email})

        user = db.query(User).filter(User.email == email).first()
        if not user:
            flash(request, 'Account not found.', 'danger')
            return RedirectResponse(url='/reset-password', status_code=status.HTTP_303_SEE_OTHER)

        user.password_hash = generate_password_hash(new_password)
        db.commit()
        request.session.pop('user_id', None)
        flash(request, 'Your password has been successfully reset. Please log in.', 'success')
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    # Flow B: No token -> Request reset link for an email address
    email = form.get('email', '').strip().lower()
    if not email:
        flash(request, 'Email address is required.', 'danger')
        return RedirectResponse(url='/reset-password', status_code=status.HTTP_303_SEE_OTHER)

    user = db.query(User).filter(User.email == email).first()
    if user:
        reset_token = generate_reset_token(user.email, secret_key)
        base_url = str(request.base_url).rstrip('/')
        reset_url = f"{base_url}/reset-password/{reset_token}"

        # Log link for development and audit trails
        logger.info("Password reset token generated for [%s]. Reset URL: %s", user.email, reset_url)

        # TODO: Wire up email sending service (SMTP / SendGrid / Resend)
        # Example: send_email(to=user.email, subject="Reset Password", body=f"Reset link: {reset_url}")

    flash(request, 'If that email is registered, a password reset link has been dispatched.', 'info')
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/logout')
async def logout(request: Request, current_user: User = Depends(login_required)):
    request.session.pop('user_id', None)
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)


# ── Prediction Form ───────────────────────────────────────────────────────────
@router.get('/form')
async def fitness_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(login_required)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return render_template(request, 'index.html', {'user': current_user, 'profile': profile})


# ── Prediction ────────────────────────────────────────────────────────────────
@router.post('/predict')
async def predict(request: Request, db: Session = Depends(get_db), current_user: User = Depends(login_required)):
    form = dict(await request.form())
    verify_csrf(request, form)

    data, error = validate_predict_form(form)
    if error:
        flash(request, f'Please fix the following: {error}', 'danger')
        return RedirectResponse(url='/form', status_code=status.HTTP_303_SEE_OTHER)

    model = request.app.state.model
    try:
        bf_pct = run_prediction(data, model)
    except Exception as e:
        logger.exception("Prediction failed: %s", e)
        flash(request, 'Prediction failed. Please check your inputs and try again.', 'danger')
        return RedirectResponse(url='/form', status_code=status.HTTP_303_SEE_OTHER)

    # Save / update user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)

    profile.age               = data['age']
    profile.gender            = data['gender']
    profile.height            = data['height']
    profile.activity          = data['activity']
    profile.goal              = data['goal']
    profile.exercise_location = data['exercise_location']
    db.add(profile)

    result = Result(
        user_id=current_user.id,
        age=data['age'], gender=data['gender'], height=data['height'],
        weight=data['weight'], waist=data['waist'], neck=data['neck'],
        hip=data['hip'], sleep=data['sleep'], workouts=data['workouts'],
        calories=data['calories'], activity=data['activity'],
        goal=data['goal'], exercise_location=data['exercise_location'],
        bf_pct=bf_pct,
    )
    db.add(result)
    db.commit()

    notes     = build_notes(data['goal'], bf_pct, data['gender'])
    split     = build_split(data['workouts'])
    exercises = build_exercises(split, data['exercise_location'])
    unusual_warnings = check_training_bounds(data)

    return render_template(
        request,
        'result.html',
        {
            'bf_pct': bf_pct,
            'gender': data['gender'],
            'age': data['age'],
            'height': data['height'],
            'weight': data['weight'],
            'split': split,
            'notes': notes,
            'exercises': exercises,
            'exercise_location': data['exercise_location'],
            'unusual_warnings': unusual_warnings,
            'is_guest': False,
            'ref': '',
        }
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get('/dashboard')
async def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(login_required)):
    results = (db.query(Result)
               .filter(Result.user_id == current_user.id)
               .order_by(Result.created_at.asc())
               .all())

    # Build chart data for body fat over time
    chart_labels = [r.created_at.strftime('%b %d') for r in results]
    chart_data   = [r.bf_pct for r in results]

    # Referral link
    base_url = str(request.base_url).rstrip('/')
    referral_url = f"{base_url}/try?ref={current_user.referral_code}"

    return render_template(
        request,
        'dashboard.html',
        {
            'user': current_user,
            'results': list(reversed(results)),  # newest first for table
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'referral_url': referral_url,
        }
    )


# ── Delete Account ────────────────────────────────────────────────────────────
@router.post('/delete-account')
async def delete_account(request: Request, db: Session = Depends(get_db), current_user: User = Depends(login_required)):
    form = dict(await request.form())
    verify_csrf(request, form)

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Result).filter(Result.user_id == user.id).delete()
    db.query(UserProfile).filter(UserProfile.user_id == user.id).delete()
    db.delete(user)
    db.commit()

    request.session.pop('user_id', None)
    flash(request, 'Your account has been permanently deleted.', 'info')
    return RedirectResponse(url='/register', status_code=status.HTTP_303_SEE_OTHER)


# ── Helper ────────────────────────────────────────────────────────────────────
def _save_guest_result(request: Request, user: User, db: Session):
    """If a guest prediction was done before login/signup, save it now."""
    gr = request.session.pop('guest_result', None)
    if not gr:
        return

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
    profile.age               = gr['age']
    profile.gender            = gr['gender']
    profile.height            = gr['height']
    profile.activity          = gr['activity']
    profile.goal              = gr['goal']
    profile.exercise_location = gr['exercise_location']
    db.add(profile)

    result = Result(
        user_id=user.id,
        age=gr['age'], gender=gr['gender'], height=gr['height'],
        weight=gr['weight'], waist=gr['waist'], neck=gr['neck'],
        hip=gr['hip'], sleep=gr['sleep'], workouts=gr['workouts'],
        calories=gr['calories'], activity=gr['activity'],
        goal=gr['goal'], exercise_location=gr['exercise_location'],
        bf_pct=gr['bf_pct'],
    )
    db.add(result)
    db.commit()
