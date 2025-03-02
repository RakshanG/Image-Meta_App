from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User  # Ensure this is correctly defined

auth_bp = Blueprint('auth', __name__)

# Login Route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for("home"))
        else:
            flash('Invalid credentials', 'danger')

    return render_template("login.html")

# Register Route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        user = User.register(username, password)
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for("auth.login"))
        else:
            flash('Registration failed', 'danger')

    return render_template("register.html")

# Logout Route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout successful', 'success')
    return redirect(url_for("home"))
