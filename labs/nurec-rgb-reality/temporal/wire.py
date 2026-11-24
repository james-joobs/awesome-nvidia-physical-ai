"""Lossless response encoding; history always uses the unencoded RGB pixels."""
import io
from PIL import features


def encode_preview(image, execution):
    buffer = io.BytesIO()
    if execution != 'baseline' and features.check('webp'):
        # For lossless WebP, quality is compression effort, not pixel quality.
        image.save(buffer, format='WEBP', lossless=True, method=0, quality=0)
        mime = 'image/webp'
    else:
        image.save(buffer, format='PNG', compress_level=6 if execution == 'baseline' else 1)
        mime = 'image/png'
    return mime, buffer.getvalue()
