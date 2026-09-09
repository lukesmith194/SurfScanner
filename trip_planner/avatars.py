"""Profile picture handling: normalize any upload to a small square PNG
before storing it (see db.py — stored as bytes in the database, not on
disk, for the same persistence reason as everything else in this app).
"""

from io import BytesIO

from PIL import Image

AVATAR_SIZE = 200


def resize_avatar(uploaded_bytes: bytes) -> bytes:
    """Center-crop to a square, resize, and re-encode as PNG — keeps stored
    avatars small and consistent regardless of what was uploaded.
    """
    img = Image.open(BytesIO(uploaded_bytes)).convert("RGB")
    width, height = img.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((AVATAR_SIZE, AVATAR_SIZE))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
