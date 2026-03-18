"""
routes.py
─────────
All Flask routes. Each route is intentionally thin — heavy logic lives in utils.py.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

from extensions import db
from db_models import User, Result, UserProfile
from utils import validate_predict_form, build_notes, build_split, build_exercises

main = Blueprint('main', __name__)


# ── Home ──────────────────────────────────────────────────────────────────────

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


# ── Auth ──────────────────────────────────────────────────────────────────────
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('All fields are required.')
            return render_template('register.html')

       

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.')
            return render_template('register.html')

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.fitness_form'))

    return render_template('register.html')


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

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.')
            return redirect(url_for('main.login'))

        login_user(user)
        return redirect(url_for('main.dashboard') if user.results
                        else url_for('main.fitness_form'))

    return render_template('login.html')


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

        # Generic message — prevents email enumeration
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
    # 1. Validate all inputs
    data, error = validate_predict_form(request.form)
    if error:
        flash(f'Please fix the following: {error}')
        return redirect(url_for('main.fitness_form'))

    # 2. Run ML model
    from flask import current_app
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

    # 3. Save / update user profile
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

    # 4. Save result to history
    result = Result(
        user_id           = current_user.id,
        age               = data['age'],
        gender            = data['gender'],
        height            = data['height'],
        weight            = data['weight'],
        waist             = data['waist'],
        neck              = data['neck'],
        hip               = data['hip'],
        sleep             = data['sleep'],
        workouts          = data['workouts'],
        calories          = data['calories'],
        activity          = data['activity'],
        goal              = data['goal'],
        exercise_location = data['exercise_location'],
        bf_pct            = bf_pct,
    )
    db.session.add(result)
    db.session.commit()

    # 5. Build recommendation data
    notes     = build_notes(data['goal'], bf_pct, data['gender'])
    split     = build_split(data['workouts'])
    exercises = build_exercises(split, data['exercise_location'])

    return render_template(
        'result.html',
        bf_pct            = bf_pct,
        gender            = data['gender'],
        age               = data['age'],
        height            = data['height'],
        weight            = data['weight'],
        split             = split,
        notes             = notes,
        exercises         = exercises,
        exercise_location = data['exercise_location'],
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    results = (Result.query
               .filter_by(user_id=current_user.id)
               .order_by(Result.created_at.desc())
               .all())
    return render_template('dashboard.html', user=current_user, results=results)


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


# ── Error handlers ────────────────────────────────────────────────────────────

@main.app_errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
