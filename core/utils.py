import os
from uuid import uuid4

def profile_image_upload(instance, filename):
    """Upload path: media/profiles/<username>/<uuid>.<ext>"""
    ext = filename.split('.')[-1]
    unique_name = f"{uuid4().hex}.{ext}"
    return os.path.join("profiles", instance.username, unique_name)

