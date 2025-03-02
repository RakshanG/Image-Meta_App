from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    """User Registration Form"""
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_email(self, email):
        """Custom validator to check if the email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already registered. Please use a different one.")

class LoginForm(FlaskForm):
    """User Login Form"""
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")

class UploadForm(FlaskForm):
    """Image Upload Form"""
    file = FileField("Choose an Image", validators=[
        DataRequired(),
        FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")
    ])
    submit = SubmitField("Upload")

    def validate_file(self, file):
        """Custom file size validation (limit: 10MB)"""
        if not file.data:
            raise ValidationError("No file selected. Please choose an image.")

        file_data = file.data.read()
        if len(file_data) > 10 * 1024 * 1024:  
            raise ValidationError("File is too large. Maximum size is 10MB.")
        
        file.data.seek(0)  

class ResetPasswordForm(FlaskForm):
    """Password Reset Request Form"""
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        """Custom validator to check if the email exists."""
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Email not found. Please check your email address.")

class ResetPasswordConfirmForm(FlaskForm):
    """Password Reset Confirmation Form"""
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")