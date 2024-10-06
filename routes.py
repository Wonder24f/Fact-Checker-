from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, ClaimForm
from models import db, User, Claim, Vote

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def dashboard():
    claims = Claim.query.all()
    return render_template('dashboard.html', claims=claims)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)  # Hash password in production
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # Hash password check in production
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check username and password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/submit_claim', methods=['GET', 'POST'])
@login_required
def submit_claim():
    form = ClaimForm()
    if form.validate_on_submit():
        new_claim = Claim(statement=form.statement.data, author=current_user)
        db.session.add(new_claim)
        db.session.commit()
        flash('Claim submitted successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('submit_claim.html', form=form)

@main.route('/vote/<int:claim_id>/<string:vote_type>', methods=['POST'])
@login_required
def vote(claim_id, vote_type):
    existing_vote = Vote.query.filter_by(user_id=current_user.id, claim_id=claim_id).first()
    if existing_vote:
        flash('You have already voted on this claim.', 'warning')
    else:
        new_vote = Vote(user_id=current_user.id, claim_id=claim_id, vote_type=vote_type)
        db.session.add(new_vote)
        db.session.commit()
        flash('Vote recorded!', 'success')
    return redirect(url_for('main.dashboard'))
