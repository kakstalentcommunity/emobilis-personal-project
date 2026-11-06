import qrcode
from qrcode.image.svg import SvgPathImage
from django.conf import settings
def qr_svg(table):
    base = settings.SITE_BASE_URL.rstrip('/')
    image = qrcode.make(f'{base}/t/{table.qr_code}/', image_factory=SvgPathImage, border=3)
    import io
    output = io.BytesIO(); image.save(output)
    return output.getvalue()
