import os
import logging
import uuid
import traceback
from datetime import timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint, jsonify, send_from_directory, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy.sql import text
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, Image, ImageMetadata
from auth import auth_bp  
from forms import UploadForm, RegistrationForm  
from utils import extract_metadata, get_lat_lon, send_reset_email, allowed_file
from flask_mail import Mail


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()]
)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "your_secret_key_here"),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax"
    )

    
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri="memory://",
        default_limits=["200 per day", "50 per hour"]
    )

    
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5503", "http://127.0.0.1:5503"]}})

    
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root:8912@127.0.0.1/image_meta")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    mail = Mail(app)

    
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            logging.info("Database connection successful.")
    except Exception as e:
        logging.error(f" Database connection error: {e}")
        exit(1)

    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    app.register_blueprint(auth_bp, url_prefix="/auth")  

    
    main_bp = Blueprint("main", __name__)

    @main_bp.route("/")
    def home():
        """Force fresh session start"""
        session.clear()
        return redirect(url_for("auth.register_page"))

    @main_bp.route("/logout")
    @login_required
    def logout():
        logout_user()
        session.clear()
        flash("Logout successful", "success")
        return redirect(url_for("auth.login_page"))

    @main_bp.route("/upload", methods=["GET", "POST"])
    @login_required
    @limiter.limit("5 per minute")
    def upload_image():
        """Upload image with metadata extraction"""
        form = UploadForm()
        if form.validate_on_submit():
            file = form.file.data
            if not file or not allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
                flash("Invalid file format!", "danger")
                return redirect(url_for("main.upload_image"))

            try:
                file_ext = file.filename.rsplit(".", 1)[-1].lower()
                unique_filename = secure_filename(f"{uuid.uuid4()}.{file_ext}")
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                file.save(file_path)

                metadata = extract_metadata(file_path) or {}
                latitude, longitude = get_lat_lon(metadata)

                image = Image(
                    user_id=current_user.id,
                    filename=unique_filename,
                    file_path=file_path,
                    latitude=latitude,
                    longitude=longitude
                )
                db.session.add(image)
                db.session.flush()

                metadata_records = [
                    ImageMetadata(image_id=image.id, key_name=key, value=str(value))
                    for key, value in metadata.items()
                ]
                db.session.bulk_save_objects(metadata_records)
                db.session.commit()

                flash(" Image uploaded successfully!", "success")
                return redirect(url_for("main.get_metadata", image_id=image.id))

            except Exception as e:
                db.session.rollback()
                logging.error(f"Upload error: {str(e)}\n{traceback.format_exc()}")
                flash(f" Upload failed: {str(e)}", "danger")

        return render_template("upload.html", form=form)

    @main_bp.route("/metadata/<int:image_id>")
    @login_required
    def get_metadata(image_id):
        """Display metadata for a specific image"""
        image = Image.query.get_or_404(image_id)
        if image.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("main.home"))

        metadata = {m.key_name: m.value for m in ImageMetadata.query.filter_by(image_id=image.id).all()}
        return render_template("metadata.html", image=image, metadata=metadata)

    @main_bp.route("/clear_metadata/<int:image_id>", methods=["POST"])
    @login_required
    def clear_metadata(image_id):
        """Clear metadata for a specific image"""
        image = Image.query.get_or_404(image_id)
        if image.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("main.home"))

        try:
            
            ImageMetadata.query.filter_by(image_id=image.id).delete()
            db.session.commit()
            flash("Metadata cleared successfully!", "success")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error clearing metadata: {str(e)}\n{traceback.format_exc()}")
            flash("❌ Failed to clear metadata.", "danger")

        return redirect(url_for("main.get_metadata", image_id=image.id))

    
    @main_bp.route("/uploads/<filename>")
    def serve_image(filename):
        """Serve uploaded images"""
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    
    @main_bp.route('/download_metadata/<int:image_id>')
    @login_required
    def download_metadata(image_id):
        """Download metadata as a JSON file"""
        image = Image.query.get_or_404(image_id)
        if image.user_id != current_user.id:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("main.home"))

        metadata = {m.key_name: m.value for m in ImageMetadata.query.filter_by(image_id=image.id).all()}
        return jsonify(metadata), 200, {'Content-Disposition': f'attachment; filename=metadata_{image.id}.json'}

    
    app.register_blueprint(main_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5503)