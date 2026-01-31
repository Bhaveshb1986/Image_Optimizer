"""
Flask routes for the Image Optimizer application.

This module defines the main web interface and API for uploading images,
processing them (resize and JPEG compression via OpenCV), and serving
the processed files. It uses a single Blueprint, ``main_bp``, which
should be registered on the Flask application.

Routes
------
- ``/``
    Renders the index page (HTML).
- ``POST /upload``
    Accepts an image file and optional ``quality`` form field; resizes
    to 50%, saves as JPEG, and returns JSON with success message,
    processed filename, and size reduction stats.
- ``/uploads/<filename>``
    Serves files from the configured upload directory (processed images).
- ``/favicon.ico``
    Returns 204 No Content to avoid favicon 404s.

Configuration
-------------
The app must set ``config['UPLOAD_FOLDER']`` to the directory used for
temporary and processed image storage.

Dependencies
------------
Uses OpenCV (cv2) for resize/compression, Pillow (PIL) for image
validation, and Flask for routing and request handling.
"""
import os
import cv2
from PIL import Image, UnidentifiedImageError
from flask import Blueprint, request, current_app, jsonify, render_template, send_from_directory

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Renders the index page.
    """
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload():
    """
    Handles the upload of an image file via a POST request.
    This function accepts an image file from the request, processes it with OpenCV (resizes to 50%),
    saves the processed image to a local directory, and returns a JSON response.
    Returns:
        JSON: A dictionary containing a success message and processed image path if successful.
        JSON: A dictionary containing an error message and appropriate status code on failure.
    Notes:
        - The uploaded image is processed using OpenCV to resize to 50% of original size.
        - The processed image is saved to the directory specified by the 'UPLOAD_FOLDER' key
          in the application's configuration.
        - The image file is retrieved from the 'image' key in the request's files.
    """
    try:
        image_file = request.files.get('image')

        if not image_file:
            return jsonify({'error': 'No image uploaded!'}), 400

        # Ensure upload folder exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        try:
            os.makedirs(upload_folder, exist_ok=True)
        except OSError as e:
            current_app.logger.error(f"Failed to create upload folder: {e}")
            return jsonify({'error': 'Server error: Unable to prepare upload directory.'}), 500

        # Check if the uploaded file is an image
        allowed_extensions = {"png", "jpg", "jpeg", "gif"}
        allowed_mime_types = {"image/png", "image/jpeg", "image/gif"}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

        if not allowed_file(image_file.filename):
            return jsonify({'error': 'Invalid file type! Only image files are allowed.'}), 400

        # Save temp file and verify it's an image using Pillow (content-based)
        temp_path = os.path.join(upload_folder, 'temp_' + image_file.filename)
        try:
            image_file.save(temp_path)
        except Exception as e:
            current_app.logger.error(f"Failed to save temp file: {e}")
            return jsonify({'error': 'Server error: Unable to save uploaded file.'}), 500

        try:
            with Image.open(temp_path) as im:
                im.verify()  # verify that it's an image
        except (UnidentifiedImageError, OSError) as e:
            current_app.logger.warning(f"Uploaded file is not a valid image: {e}")
            try:
                os.remove(temp_path)
            except OSError:
                pass
            return jsonify({'error': 'Uploaded file is not a valid image!'}), 400
        except Exception as e:
            current_app.logger.error(f"Error verifying image file: {e}")
            try:
                os.remove(temp_path)
            except OSError:
                pass
            return jsonify({'error': 'Server error: Unable to verify file type.'}), 500

        # Get quality parameter from form, default to 50
        try:
            quality = int(request.form.get('quality', 50))
            if quality < 0 or quality > 100:
                quality = 50  # Default if out of range
        except ValueError:
            quality = 50

        # Process with OpenCV: resize to 50%
        try:
            image = cv2.imread(temp_path)
            if image is None:
                os.remove(temp_path)
                return jsonify({'error': 'Invalid image file!'}), 400

            height, width = image.shape[:2]
            new_width = int(width * 0.5)
            new_height = int(height * 0.5)
            resized_image = cv2.resize(image, (new_width, new_height))
        except Exception as e:
            current_app.logger.error(f"OpenCV processing error: {e}")
            os.remove(temp_path)
            return jsonify({'error': 'Server error: Unable to process image.'}), 500

        # Always save as JPEG with the specified quality for compression
        compression_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        output_ext = 'jpg'

        # Save processed image
        base_name = os.path.splitext(image_file.filename)[0]
        processed_filename = f'processed_{base_name}.{output_ext}'
        processed_path = os.path.join(upload_folder, processed_filename)
        try:
            cv2.imwrite(processed_path, resized_image, compression_params)
        except Exception as e:
            current_app.logger.error(f"Failed to save processed image: {e}")
            os.remove(temp_path)
            return jsonify({'error': 'Server error: Unable to save processed image.'}), 500

        # Get file sizes
        original_size = os.path.getsize(temp_path)
        processed_size = os.path.getsize(processed_path)
        size_reduction = ((original_size - processed_size) / original_size) * 100 if original_size > 0 else 0

        # Clean up temp file
        try:
            os.remove(temp_path)
        except OSError as e:
            current_app.logger.warning(f"Failed to remove temp file: {e}")

        return jsonify({
            'message': 'Image uploaded and processed successfully!',
            'processed_image': processed_filename,
            'original_size': original_size,
            'processed_size': processed_size,
            'size_reduction_percent': round(size_reduction, 2)
        })
    except Exception as e:
        current_app.logger.error(f"Unexpected error in upload route: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serves uploaded files from the upload folder.
    This route allows the browser to access processed images by their filename.
    It uses Flask's send_from_directory to securely serve files from the configured upload directory.
    """
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        current_app.logger.warning(f"File not found: {filename}")
        return jsonify({'error': 'File not found.'}), 404
    except Exception as e:
        current_app.logger.error(f"Error serving file {filename}: {e}")
        return jsonify({'error': 'Server error: Unable to serve file.'}), 500

@main_bp.route('/favicon.ico')
def favicon():
    """
    Handles favicon requests by returning 204 No Content to avoid 404 errors.
    """
    return '', 204
