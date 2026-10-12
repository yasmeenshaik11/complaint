import os, uuid
from werkzeug.utils import secure_filename
from PIL import Image
ALLOWED = {'jpg','jpeg','png','webp'}
def save_image(file, upload_folder):
    if not file or not file.filename: return None
    ext = file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED: raise ValueError('Only JPG, JPEG, PNG and WEBP images are allowed.')
    try:
        img = Image.open(file); img.verify()
    except Exception: raise ValueError('Uploaded file is not a valid image.')
    filename = secure_filename(f'{uuid.uuid4().hex}.{ext}')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return f'/static/uploads/{filename}'
