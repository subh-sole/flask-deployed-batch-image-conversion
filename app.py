import os
import zipfile
from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)

MAX_UPLOAD_FILES = 10
MAX_FILE_SIZE_MB = 20
FORMAT_CHOICES = ['TIFF', 'JPEG', 'PNG', 'BMP', 'GIF', 'WEBP']
FORMAT_EXTENSIONS = {
    'TIFF': ('.tif', '.tiff'),
    'JPEG': ('.jpg', '.jpeg'),
    'PNG': ('.png',),
    'BMP': ('.bmp',),
    'GIF': ('.gif',),
    'WEBP': ('.webp',),
}

# Set the temporary folder to store uploaded files and converted images
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Check if the temporary folders exist; if not, create them
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CONVERTED_FOLDER):
    os.makedirs(CONVERTED_FOLDER)

# Clear old temp files when the app starts so each run begins clean.
def clear_temp_folders():
    for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

clear_temp_folders()

# Lightweight server-side validation for uploaded image files.
# This is not a full antivirus scanner, but it catches obvious invalid or malicious files.
def get_file_signature_matches(file_bytes, allowed_extensions):
    if not file_bytes:
        return False

    extension_set = {ext.lower() for ext in allowed_extensions}
    signature_checks = {
        '.jpg': (b'\xff\xd8\xff',),
        '.jpeg': (b'\xff\xd8\xff',),
        '.png': (b'\x89PNG\r\n\x1a\n',),
        '.gif': (b'GIF87a', b'GIF89a'),
        '.bmp': (b'BM',),
        '.tif': (b'II*\x00', b'MM\x00*'),
        '.tiff': (b'II*\x00', b'MM\x00*'),
        '.webp': (b'RIFF',),
    }

    for ext in extension_set:
        if ext in signature_checks:
            for marker in signature_checks[ext]:
                if file_bytes.startswith(marker):
                    return True

    if b'RIFF' in file_bytes[:12] and b'WEBP' in file_bytes[:12]:
        return True

    return False


def contains_suspicious_content(file_bytes):
    suspicious_markers = (
        b'MZ', b'PK\x03\x04', b'#!/', b'<script', b'<?php', b'<?xml',
        b'ELF', b'7z\xbc\xaf\x27\x1c', b'javascript:', b'vbscript:'
    )
    sample = file_bytes[:8192].lower()
    for marker in suspicious_markers:
        if marker.lower() in sample:
            return True
    return False


def validate_uploaded_image(file):
    if file is None or not hasattr(file, 'filename') or not file.filename:
        return False, 'No file selected.'

    if file.content_length is not None and file.content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f'File exceeds the {MAX_FILE_SIZE_MB} MB limit.'

    original_name = file.filename.lower()
    allowed_exts = tuple(ext.lower() for ext in FORMAT_EXTENSIONS.get(request.form.get('source_format', 'TIFF'), ()))
    if not original_name.endswith(allowed_exts):
        return False, f'Only {", ".join(allowed_exts)} files are allowed for the selected format.'

    file_bytes = file.read()
    file.seek(0)

    if not file_bytes:
        return False, 'Uploaded file is empty.'

    if contains_suspicious_content(file_bytes):
        return False, 'Uploaded file contains suspicious executable/script content.'

    if not get_file_signature_matches(file_bytes, allowed_exts):
        return False, 'The uploaded file does not match the selected image type.'

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return False, 'The uploaded file is not a valid image.'

    return True, 'Valid image file.'


def convert_to_format(source_path, output_path, output_format):
    with Image.open(source_path) as image:
        if output_format in ('JPEG', 'PNG', 'BMP', 'WEBP', 'TIFF', 'GIF'):
            if output_format == 'JPEG':
                rgb_image = image.convert('RGB')
                rgb_image.save(output_path, format='JPEG')
            else:
                image.convert('RGBA' if output_format == 'PNG' else 'RGB').save(output_path, format=output_format)


def get_output_extension(output_format):
    return {
        'TIFF': '.tiff',
        'JPEG': '.jpeg',
        'PNG': '.png',
        'BMP': '.bmp',
        'GIF': '.gif',
        'WEBP': '.webp',
    }.get(output_format, '.png')

@app.route('/')
def index():
    # Get the list of uploaded files
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', uploaded_files=uploaded_files)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files')
    source_format = request.form.get('source_format', 'TIFF')
    target_format = request.form.get('target_format', 'JPEG')

    if not uploaded_files or all(file.filename == '' for file in uploaded_files):
        return jsonify({"status": "error", "message": "No files selected"}), 400

    if len(uploaded_files) > MAX_UPLOAD_FILES:
        return jsonify({"status": "error", "message": f"Please upload no more than {MAX_UPLOAD_FILES} files at a time."}), 400

    if source_format == target_format:
        return jsonify({"status": "error", "message": "Source and target formats must be different."}), 400

    allowed_extensions = FORMAT_EXTENSIONS.get(source_format, ())
    successful = []
    failed = []

    for file in uploaded_files:
        if file.filename == '':
            continue

        is_valid, message = validate_uploaded_image(file)
        if not is_valid:
            failed.append(f"{file.filename} ({message})")
            continue

        lower_name = file.filename.lower()
        if not lower_name.endswith(allowed_extensions):
            failed.append(file.filename)
            continue

        if file.content_length is not None and file.content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
            failed.append(file.filename)
            continue

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        output_name = os.path.splitext(file.filename)[0] + get_output_extension(target_format)
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_name)
        convert_to_format(file_path, output_path, target_format)
        successful.append(file.filename)

    if successful and not failed:
        return jsonify({"status": "success", "message": f"{len(successful)} file(s) converted from {source_format} to {target_format} successfully!"})
    if successful and failed:
        return jsonify({"status": "warning", "message": f"{len(successful)} file(s) converted successfully. Some files were skipped: {', '.join(failed)}"})
    return jsonify({"status": "error", "message": f"No valid {source_format} files were uploaded for conversion to {target_format}. Invalid files: {', '.join(failed)}"}), 400

@app.route('/download')
def download():
    # Create a zip file containing all the converted .jpeg files
    converted_files = os.listdir(app.config['CONVERTED_FOLDER'])
    zip_path = 'converted_files.zip'
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file in converted_files:
            file_path = os.path.join(app.config['CONVERTED_FOLDER'], file)
            zip_file.write(file_path, file)

    # Return the zip file for download
    return send_file(zip_path, as_attachment=True)

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    # Remove all files from both temporary folders so the app resets cleanly.
    for folder in [app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER']]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    return jsonify({"status": "success", "message": "Uploads and converted files cleared successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
