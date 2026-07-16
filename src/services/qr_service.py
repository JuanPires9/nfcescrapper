import cv2
import numpy as np
from PIL import Image
import io

try:
    import zxingcpp
except ImportError:
    zxingcpp = None


def extract_qr_from_image(file_bytes: bytes) -> str | None:
    """
    Extrai URL do QR Code usando zxing-cpp como principal e OpenCV como fallback.
    """
    image = Image.open(io.BytesIO(file_bytes))

    # 1. Tenta usar o zxing-cpp (mais robusto)
    if zxingcpp:
        try:
            results = zxingcpp.read_barcodes(image)
            if results:
                return results[0].text
        except Exception:
            pass

    # 2. Fallback para OpenCV
    try:
        open_cv_image = np.array(image)
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(open_cv_image)
        if data:
            return data
    except Exception:
        pass

    return None