import logging
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


db = SQLAlchemy()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    
    images = db.relationship('Image', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, email, password=None, **kwargs):
        super().__init__(**kwargs)
        self.email = email.lower().strip()
        if password:
            self.set_password(password)

    def set_password(self, password):
        """Hash and set the user's password."""
        if not password:
            raise ValueError("Password cannot be empty.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_id(cls, user_id):
        """Retrieve a user by their ID."""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """Retrieve a user by their email."""
        return cls.query.filter_by(email=email.lower().strip()).first()

    @classmethod
    def create(cls, email, password):
        """Create a new user."""
        email = email.lower().strip()
        if cls.get_by_email(email):
            logger.warning(f"Registration attempt with existing email: {email}")
            raise ValueError("Email already exists!")

        user = cls(email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User '{email}' successfully created.")
            return user
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Integrity error while creating user '{email}'")
            raise ValueError("Email is already in use.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while creating user '{email}': {str(e)}")
            raise ValueError("An unexpected error occurred. Please try again.")

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate a user."""
        email = email.lower().strip()
        user = cls.get_by_email(email)
        if user and user.check_password(password):
            logger.info(f"User '{email}' authenticated successfully.")
            return user
        logger.warning(f"Failed authentication attempt for email: {email}")
        return None

    def __repr__(self):
        return f"<User {self.email}>"



class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_extension = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    
    image_metadata = db.relationship('ImageMetadata', backref='image', lazy=True, cascade="all, delete-orphan")

    def __init__(self, user_id, filename, file_path, latitude=None, longitude=None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.filename = filename
        self.file_path = file_path
        self.file_extension = os.path.splitext(filename)[1].lower().strip('.')
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"<Image {self.filename} (User {self.user_id})>"

    @classmethod
    def create(cls, user_id, filename, file_path, latitude=None, longitude=None):
        """Create a new image entry."""
        valid_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'}
        file_ext = filename.rsplit('.', 1)[-1].lower()
        if file_ext not in valid_extensions:
            raise ValueError(f"Invalid file extension. Allowed extensions are: {', '.join(valid_extensions)}")

        image = cls(user_id=user_id, filename=filename, file_path=file_path, latitude=latitude, longitude=longitude)
        try:
            db.session.add(image)
            db.session.commit()
            logger.info(f"Image '{filename}' added successfully for user '{user_id}'.")
            return image
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while adding image '{filename}' for user '{user_id}': {str(e)}")
            raise ValueError("Error occurred while saving image. Please try again.")



class ImageMetadata(db.Model):
    __tablename__ = 'image_metadata'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    key_name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, image_id, key_name, value, **kwargs):
        super().__init__(**kwargs)
        self.image_id = image_id
        self.key_name = key_name
        self.value = value

    def __repr__(self):
        return f"<ImageMetadata {self.key_name}: {self.value}>"

    @classmethod
    def create(cls, image_id, key_name, value):
        """Create a new metadata entry for an image."""
        metadata = cls(image_id=image_id, key_name=key_name, value=value)
        try:
            db.session.add(metadata)
            db.session.commit()
            logger.info(f"Metadata '{key_name}' for image ID {image_id} added successfully.")
            return metadata
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while adding metadata for image ID {image_id}: {str(e)}")
            raise ValueError("Error occurred while saving metadata. Please try again.")