# Image-Meta_App

# Overview :
The Image Meta App is a Flask-based web application that allows users to upload images and extract metadata including EXIF data and GPS coordinates. Users can register and log in to manage their image uploads and view metadata history. 

# Features :
1. User Authentication: Register, login, and logout functionality.
2. Image Upload: Users can upload images for metadata extraction.
3. Metadata Extraction: Extracts EXIF data such as camera model, timestamp, and GPS location.
4. Metadata Display: Displays extracted metadata in a structured format.
5. Database Integration: Stores user-uploaded images and metadata in a MySQL database.
6. History Log: Maintains a history of uploaded images and extracted metadata for each user.
7. RESTful API Endpoints: API endpoints for authentication, image upload, and metadata retrieval.

# Installation & Setup :
Installation & Setup
Prerequisites
Ensure you have the following installed:
1.Python 3.x
2.Flask and required dependencies
3.MySQL Server

Clone the Repository : git clone https://github.com/RakshanG/Image-Meta_App.git
cd Image-Meta_App

Install Dependencies : pip install -r requirements.txt

# Database Setup :
1. Create a MySQL database : CREATE DATABASE image_meta_db;
2. Import the schema : mysql -u your_username -p image_meta_db < Users.sql
3. Configure database credentials in .env file : DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=image_meta_db

# Running the Application : 
python app.py

# API Endpoints :

/register - POST - Register a new user 
/login - POST - Authenticate user 
/upload - POST - Upload an image for metadata extraction
/metadata - GET - Retrieve metadata for uploaded images 
/logout - GET - Log out the user

# Technologies Used :
1. Backend : Flask, SQLAlchemy
2. Frontend : Bootstrap, HTML, CSS
3. Database : MySQL
4. Libraries: Pillow, Flask-Login

# Contribution :
You can fork this repository and submit pull requests. 


