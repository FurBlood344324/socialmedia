import os
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
import time

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{int(time.time())}_{filename}"
        
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file.save(os.path.join(upload_folder, filename))
        
        file_url = url_for('static', filename=f'uploads/{filename}', _external=True)
        
        return jsonify({'url': file_url}), 201
        
    return jsonify({'error': 'File type not allowed'}), 400


@upload_bp.route('/generate-avatar', methods=['POST'])
def generate_avatar():
    """
    Generates a default avatar for the given username and assigns it to the user.
    Expects JSON: {"username": "foo"}
    """
    from api.services.user_service import UserService
    from api.utils.avatar_generator import generate_initial_avatar

    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        user_service = UserService()
        
        user = user_service.get_user(username=username)
        if not user:
             return jsonify({'error': 'User not found'}), 404

        avatar_url = generate_initial_avatar(username)

        result = user_service.update_profile(user['user_id'], {'profile_picture_url': avatar_url})

        if not result['success']:
             return jsonify({'error': result['error']}), 500

        return jsonify({'url': avatar_url, 'message': 'Avatar generated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

