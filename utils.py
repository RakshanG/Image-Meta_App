import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from flask_mail import Message
from extensions import mail


logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    """
    Check if a filename has an allowed extension.

    Args:
        filename (str): The name of the file.
        allowed_extensions (set): A set of allowed file extensions (e.g., {"png", "jpg", "jpeg", "gif"}).

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in allowed_extensions

def get_exif_data(image_path):
    """
    Extracts EXIF data from an image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the EXIF metadata, or None if no data is found.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                metadata = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id in value:
                            sub_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[sub_tag] = value[gps_tag_id]
                        metadata[tag] = gps_data
                    else:
                        metadata[tag] = value
                return metadata
            else:
                logger.warning(f"No EXIF data found in {image_path}.")
                return None
    except Exception as e:
        logger.error(f"Error extracting EXIF data from {image_path}: {e}")
        return None

def convert_gps_to_degrees(gps_coord):
    """
    Converts GPS coordinates from degrees, minutes, seconds (DMS) to decimal degrees.

    Args:
        gps_coord (tuple): GPS coordinates in DMS format.

    Returns:
        float: GPS coordinates in decimal degrees, or None if conversion fails.
    """
    if not gps_coord:
        return None
    try:
        deg = gps_coord[0][0] / gps_coord[0][1]
        minute = gps_coord[1][0] / gps_coord[1][1]
        sec = gps_coord[2][0] / gps_coord[2][1]
        return deg + (minute / 60) + (sec / 3600)
    except Exception as e:
        logger.error(f"Error converting GPS coordinates: {e}")
        return None

def get_lat_lon(exif_data):
    """
    Extracts latitude and longitude from EXIF data.

    Args:
        exif_data (dict): EXIF metadata containing GPS information.

    Returns:
        tuple: A tuple containing (latitude, longitude), or (None, None) if not found.
    """
    if exif_data and "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        lat = convert_gps_to_degrees(gps_info.get("GPSLatitude"))
        lon = convert_gps_to_degrees(gps_info.get("GPSLongitude"))
        lat_ref = gps_info.get("GPSLatitudeRef")
        lon_ref = gps_info.get("GPSLongitudeRef")

        if lat and lon and lat_ref and lon_ref:
            if lat_ref != "N":
                lat = -lat
            if lon_ref != "E":
                lon = -lon
            return lat, lon
    logger.warning("No valid GPS data found in EXIF metadata.")
    return None, None

def extract_metadata(image_path):
    """
    Extracts metadata including GPS information from an image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: A dictionary containing the extracted metadata.
    """
    metadata = get_exif_data(image_path)
    if metadata:
        
        lat, lon = get_lat_lon(metadata)
        if lat and lon:
            metadata["latitude"] = lat
            metadata["longitude"] = lon

        
        metadata["camera_make"] = metadata.get("Make", "N/A")
        metadata["camera_model"] = metadata.get("Model", "N/A")

        
        metadata["exposure_time"] = metadata.get("ExposureTime", "N/A")
        metadata["f_number"] = metadata.get("FNumber", "N/A")
        metadata["iso"] = metadata.get("ISOSpeedRatings", "N/A")

        
        metadata["date_time"] = metadata.get("DateTimeOriginal", "N/A")

    return metadata if metadata else {}

def send_reset_email(email, token, reset_url_template="http://yourdomain.com/auth/reset_password/{token}"):
    """
    Sends a password reset email to the user.

    Args:
        email (str): The recipient's email address.
        token (str): The password reset token.
        reset_url_template (str): A template string for the reset URL, where {token} will be replaced.

    Raises:
        Exception: If sending the email fails.
    """
    try:
        subject = "Password Reset Request"
        reset_url = reset_url_template.format(token=token)
        body = f"""
        You have requested to reset your password. Please click the link below to reset your password:
        {reset_url}

        If you did not request this, please ignore this email.
        """
        
        msg = Message(subject, recipients=[email], body=body)
        mail.send(msg)
        logger.info(f"Password reset email sent to {email}.")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise