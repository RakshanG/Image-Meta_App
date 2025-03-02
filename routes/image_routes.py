from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from utils import get_exif_data, get_lat_lon
import json
import io

image_bp = Blueprint('image', __name__)

@image_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", 'danger')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            if '.' not in filename or filename.rsplit('.', 1).lower() not in {'jpg', 'jpeg', 'png', 'gif'}:
                flash("Invalid file type. Only image files are allowed.", 'danger')
                return redirect(request.url)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
            except Exception as e:
                flash(f"Error saving file: {e}", 'danger')
                return redirect(request.url)

            exif_data = get_exif_data(filepath)
            lat, lon = get_lat_lon(exif_data)

            try:
                current_app.db['images'].insert_one({
                    'user_id': current_user.id,
                    'filename': filename,
                    'metadata': exif_data,
                    'latitude': lat,
                    'longitude': lon,
                    'filepath': filepath
                })
            except Exception as e:
                flash(f"Database error: {e}", "danger")
                os.remove(filepath) #remove file if database insert fails.
                return redirect(request.url)

            return redirect(url_for('image.view_metadata', filename=filename))
    return render_template('index.html')

@image_bp.route('/view_metadata/<filename>')
@login_required
def view_metadata(filename):
    image_data = current_app.db['images'].find_one({'user_id': current_user.id, 'filename': filename})
    if image_data:
        return render_template('metadata.html', image=image_data)
    else:
        flash("Image not found", "danger")
        return redirect(url_for('image.history'))

@image_bp.route('/history')
@login_required
def history():
    user_images = list(current_app.db['images'].find({'user_id': current_user.id}))
    return render_template('history.html', images=user_images)

@image_bp.route('/api/history')
@login_required
def api_history():
    user_images = list(current_app.db['images'].find({'user_id': current_user.id}))
    return jsonify(user_images)

@image_bp.route('/api/download/<filename>')
@login_required
def api_download(filename):
    image_data = current_app.db['images'].find_one({'user_id': current_user.id, 'filename': filename})
    if image_data:
        metadata_json = json.dumps(image_data['metadata'], indent=4, default=str)
        return send_file(io.BytesIO(metadata_json.encode('utf-8')), as_attachment=True, download_name=f"{filename}_metadata.json")
    else:
        flash("Image not found", "danger")
        return redirect(url_for('image.history'))