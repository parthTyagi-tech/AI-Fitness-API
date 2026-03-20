"""
routes.py
─────────
All Flask routes. Each route is intentionally thin — heavy logic lives in utils.py.

NEW FEATURES:
  - Guest prediction (try before signup)
  - Google OAuth login
  - Shareable result cards (PNG via html2canvas)
  - Referral system
  - Progress chart on dashboard
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort, session, jsonify, current_app)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

from extensions import db, oauth
from db_models import User, Result, UserProfile
from utils import validate_predict_form, build_notes, build_split, build_exercises

main = Blueprint('main', __name__)


# ── Home ──────────────────────────────────────────────────────────────────────
@main.route('/')
def home():
    # Guests land on the form directly (try before signup)
    if current_user.is_authenticated:
        return redirect(url_for('main.fitness_form'))
    return redirect(url_for('main.guest_form'))


# ── Guest prediction (no login required) ─────────────────────────────────────
@main.route('/try', methods=['GET'])
def guest_form():
    if current_user.is_authenticated:
        return redirect(url_for('main.fitness_form'))
    ref = request.args.get('ref', '')
    return render_template('guest_form.html', ref=ref)


@main.route('/try/predict', methods=['POST'])
def guest_predict():
    """Run prediction for a guest. Store result in session, prompt sign-up."""
    data, error = validate_predict_form(request.form)
    if error:
        flash(f'Please fix the following: {error}')
        return redirect(url_for('main.guest_form'))

    model = current_app.config['MODEL']
    try:
        person = pd.DataFrame([{
            'age':               data['age'],
            'gender':            data['gender'],
            'height_cm':         data['height'],
            'weight_kg':         data['weight'],
            'waist_cm':          data['waist'],
            'neck_cm':           data['neck'],
            'hip_cm':            data['hip'],
            'sleep_hours':       data['sleep'],
            'workouts_per_week': data['workouts'],
            'daily_calories':    data['calories'],
            'activity_level':    data['activity'],
            'fitness_goal':      data['goal'],
        }])
        bf_pct = round(float(model.predict(person)[0]), 2)
    except Exception:
        flash('Prediction failed. Please check your inputs and try again.')
        return redirect(url_for('main.guest_form'))

    # Store in session so we can save it after sign-up
    session['guest_result'] = {**data, 'bf_pct': bf_pct}

    notes     = build_notes(data['goal'], bf_pct, data['gender'])
    split     = build_split(data['workouts'])
    exercises = build_exercises(split, data['exercise_location'])

    ref = request.form.get('ref', '')

    return render_template(
        'result.html',
        bf_pct=bf_pct, gender=data['gender'], age=data['age'],
        height=data['height'], weight=data['weight'],
        split=split, notes=notes, exercises=exercises,
        exercise_location=data['exercise_location'],
        is_guest=True, ref=ref,
    )


# ── Auth ──────────────────────────────────────────────────────────────────────
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        ref_code = request.form.get('ref', '').strip()

        if not name or not email or not password:
            flash('All fields are required.')
            return render_template('register.html', ref=ref_code)

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.')
            return render_template('register.html', ref=ref_code)

        # Handle referral
        referrer = None
        if ref_code:
            referrer = User.query.filter_by(referral_code=ref_code).first()

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            referred_by=referrer.id if referrer else None,
        )
        db.session.add(user)

        if referrer:
            referrer.referral_count = (referrer.referral_count or 0) + 1

        db.session.commit()

        # Save any guest prediction that was done before sign-up
        _save_guest_result(user)

        login_user(user)
        return redirect(url_for('main.fitness_form'))

    ref = request.args.get('ref', '')
    return render_template('register.html', ref=ref)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email and password are required.')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.password_hash or \
                not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.')
            return redirect(url_for('main.login'))

        login_user(user)
        _save_guest_result(user)
        return redirect(url_for('main.dashboard') if user.results
                        else url_for('main.fitness_form'))

    return render_template('login.html')


# ── Google OAuth ──────────────────────────────────────────────────────────────
@main.route('/auth/google')
def google_login():
    ref = request.args.get('ref', '')
    session['oauth_ref'] = ref
    redirect_uri = url_for('main.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@main.route('/auth/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
            userinfo = resp.json()
    except Exception as e:
        flash('Google login failed. Please try again.')
        return redirect(url_for('main.login'))

    google_id = userinfo.get('sub')
    email     = userinfo.get('email', '').lower()
    name      = userinfo.get('name', email.split('@')[0])

    # Find or create user
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id   # link existing account
        else:
            ref_code = session.pop('oauth_ref', '')
            referrer = None
            if ref_code:
                referrer = User.query.filter_by(referral_code=ref_code).first()
            user = User(
                name=name, email=email,
                google_id=google_id,
                referred_by=referrer.id if referrer else None,
            )
            db.session.add(user)
            if referrer:
                referrer.referral_count = (referrer.referral_count or 0) + 1
        db.session.commit()

    login_user(user)
    _save_guest_result(user)
    return redirect(url_for('main.dashboard') if user.results
                    else url_for('main.fitness_form'))


@main.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email        = request.form.get('email', '').strip().lower()
        new_password = request.form.get('password', '').strip()

        if not email or not new_password:
            flash('Both fields are required.')
            return redirect(url_for('main.reset_password'))

        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

        flash('If that email is registered, the password has been updated.')
        return redirect(url_for('main.login'))

    return render_template('reset_password.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ── Prediction Form ───────────────────────────────────────────────────────────
@main.route('/form')
@login_required
def fitness_form():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('index.html', user=current_user, profile=profile)


# ── Prediction ────────────────────────────────────────────────────────────────
@main.route('/predict', methods=['POST'])
@login_required
def predict():
    data, error = validate_predict_form(request.form)
    if error:
        flash(f'Please fix the following: {error}')
        return redirect(url_for('main.fitness_form'))

    model = current_app.config['MODEL']

    try:
        person = pd.DataFrame([{
            'age':               data['age'],
            'gender':            data['gender'],
            'height_cm':         data['height'],
            'weight_kg':         data['weight'],
            'waist_cm':          data['waist'],
            'neck_cm':           data['neck'],
            'hip_cm':            data['hip'],
            'sleep_hours':       data['sleep'],
            'workouts_per_week': data['workouts'],
            'daily_calories':    data['calories'],
            'activity_level':    data['activity'],
            'fitness_goal':      data['goal'],
        }])
        bf_pct = round(float(model.predict(person)[0]), 2)
    except Exception:
        flash('Prediction failed. Please check your inputs and try again.')
        return redirect(url_for('main.fitness_form'))

    # Save / update user profile
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)

    profile.age               = data['age']
    profile.gender            = data['gender']
    profile.height            = data['height']
    profile.activity          = data['activity']
    profile.goal              = data['goal']
    profile.exercise_location = data['exercise_location']
    db.session.add(profile)

    result = Result(
        user_id=current_user.id,
        age=data['age'], gender=data['gender'], height=data['height'],
        weight=data['weight'], waist=data['waist'], neck=data['neck'],
        hip=data['hip'], sleep=data['sleep'], workouts=data['workouts'],
        calories=data['calories'], activity=data['activity'],
        goal=data['goal'], exercise_location=data['exercise_location'],
        bf_pct=bf_pct,
    )
    db.session.add(result)
    db.session.commit()

    notes     = build_notes(data['goal'], bf_pct, data['gender'])
    split     = build_split(data['workouts'])
    exercises = build_exercises(split, data['exercise_location'])

    return render_template(
        'result.html',
        bf_pct=bf_pct, gender=data['gender'], age=data['age'],
        height=data['height'], weight=data['weight'],
        split=split, notes=notes, exercises=exercises,
        exercise_location=data['exercise_location'],
        is_guest=False, ref='',
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────
@main.route('/dashboard')
@login_required
def dashboard():
    results = (Result.query
               .filter_by(user_id=current_user.id)
               .order_by(Result.created_at.asc())
               .all())

    # Build chart data for body fat over time
    chart_labels = [r.created_at.strftime('%b %d') for r in results]
    chart_data   = [r.bf_pct for r in results]

    # Referral link
    referral_url = url_for('main.guest_form', ref=current_user.referral_code, _external=True)

    return render_template(
        'dashboard.html',
        user=current_user,
        results=list(reversed(results)),  # newest first for table
        chart_labels=chart_labels,
        chart_data=chart_data,
        referral_url=referral_url,
    )


# ── Delete Account ────────────────────────────────────────────────────────────
@main.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    if not user:
        abort(404)

    Result.query.filter_by(user_id=user.id).delete()
    UserProfile.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()

    logout_user()
    flash('Your account has been permanently deleted.')
    return redirect(url_for('main.register'))


# ── Helper ────────────────────────────────────────────────────────────────────
def _save_guest_result(user):
    """If a guest prediction was done before login/signup, save it now."""
    gr = session.pop('guest_result', None)
    if not gr:
        return

    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
    profile.age               = gr['age']
    profile.gender            = gr['gender']
    profile.height            = gr['height']
    profile.activity          = gr['activity']
    profile.goal              = gr['goal']
    profile.exercise_location = gr['exercise_location']
    db.session.add(profile)

    result = Result(
        user_id=user.id,
        age=gr['age'], gender=gr['gender'], height=gr['height'],
        weight=gr['weight'], waist=gr['waist'], neck=gr['neck'],
        hip=gr['hip'], sleep=gr['sleep'], workouts=gr['workouts'],
        calories=gr['calories'], activity=gr['activity'],
        goal=gr['goal'], exercise_location=gr['exercise_location'],
        bf_pct=gr['bf_pct'],
    )
    db.session.add(result)
    db.session.commit()
