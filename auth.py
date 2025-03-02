import logging
import traceback
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from models import User, db
from forms import RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordConfirmForm
from utils import send_reset_email
from itsdangerous import URLSafeTimedSerializer


auth_bp = Blueprint("auth", __name__)
csrf = CSRFProtect()


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
serializer = URLSafeTimedSerializer("your_secret_key_here")


@auth_bp.route("/api/register", methods=["POST"])
@csrf.exempt
def api_register():
    """Handle AJAX registration requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid request"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        
        if not all([email, password, confirm_password]):
            return jsonify({"status": "error", "message": "All fields are required"}), 400
            
        if not EMAIL_PATTERN.match(email):
            return jsonify({"status": "error", "message": "Invalid email format"}), 400
            
        if not PASSWORD_PATTERN.match(password):
            return jsonify({"status": "error", "message": "Password must contain: 8+ chars, 1 uppercase, 1 number, 1 special character"}), 400
            
        if password != confirm_password:
            return jsonify({"status": "error", "message": "Passwords do not match"}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({"status": "error", "message": "Email already exists"}), 400

        
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password)  
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "status": "success", 
            "message": "Registration successful! Redirecting...",
            "csrf_token": generate_csrf(),
            "redirect_url": url_for("auth.login_page")  
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"API Registration error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": "Registration failed"}), 500



@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    """Registration form handler"""
    if current_user.is_authenticated:
        return redirect(url_for("main.upload_image"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(email=form.email.data).first():
                flash("Email already registered", "danger")
                return redirect(url_for("auth.register_page"))

            new_user = User(
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)  
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash("Registration successful! Please login", "success")
            return redirect(url_for("auth.login_page"))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}\n{traceback.format_exc()}")
            flash("Registration failed", "danger")

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    """Login with flow validation"""
    
    if not User.query.first():
        return redirect(url_for("auth.register_page"))

    if current_user.is_authenticated:
        return redirect(url_for("main.upload_image"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Login successful", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.upload_image"))
        flash("Invalid email or password", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout user and clear session"""
    logout_user()
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Password reset request handler"""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = serializer.dumps(user.email, salt="password-reset")
            send_reset_email(user.email, token)
        flash("Password reset instructions sent", "info")
        return redirect(url_for("auth.login_page"))
    return render_template("reset_password.html", form=form)


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_confirm(token):
    """Password reset confirmation handler"""
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
    except:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("auth.reset_password"))

    form = ResetPasswordConfirmForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash("Password updated successfully", "success")
            return redirect(url_for("auth.login_page"))
    return render_template("reset_password_confirm.html", form=form)


@auth_bp.route("/api/login", methods=["POST"])
@csrf.exempt
def api_login():
    """Handle AJAX login requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid request"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        remember_me = data.get("remember_me", False)

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember_me)
            return jsonify({
                "status": "success", 
                "message": "Login successful",
                "csrf_token": generate_csrf(),
                "redirect_url": url_for("main.upload_image")
            }), 200
            
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    except Exception as e:
        logging.error(f"API Login error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": "Login failed"}), 500