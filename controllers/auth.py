from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models import User, Following, WebsiteStatus, Website

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.websites'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    if len(email) == 0:
        flash('Please provide your email address')
        return redirect(url_for('auth.signup'))

    if len(password) == 0:
        flash('Password cannot be empty')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)


@auth.route('/account/change', methods=['POST'])
@login_required
def chage_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    if len(new_password) == 0:
        flash('New password cannot be empty')
        return redirect(url_for('auth.account'))

    if check_password_hash(current_user.password, old_password):
        current_user.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
    else:
        flash('Wrong password cannot be empty')
        return redirect(url_for('auth.account'))

    return redirect(url_for('auth.account'))


@auth.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('password')
    if check_password_hash(current_user.password, password):
        followings = Following.query.filter_by(user_id=current_user.id).all()
        for f in followings:
            website = f.website
            delete_website = True if len(website.users) == 1 else False

            if delete_website:
                WebsiteStatus.query.filter_by(website_id=website.id).delete()
                ws = Website.query.get(website.id)
                db.session.delete(ws)
            else:
                db.session.delete(f)

        User.query.filter_by(id=current_user.id).delete()
        logout_user()
        db.session.commit()
    return redirect(url_for('auth.signup'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
