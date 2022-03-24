import hmac
import hashlib
import base64

DATE = "11111111"
SERVICE = "ses"
MESSAGE = "SendRawEmail"
TERMINAL = "aws4_request"
VERSION = 0x04


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def calculate_key(secret_access_key, region):
    signature = sign(("AWS4" + secret_access_key).encode("utf-8"), DATE)
    signature = sign(signature, region)
    signature = sign(signature, SERVICE)
    signature = sign(signature, TERMINAL)
    signature = sign(signature, MESSAGE)
    signature_and_version = bytes([VERSION]) + signature
    smtp_password = base64.b64encode(signature_and_version)
    return smtp_password.decode("utf-8")


def smtp_password(secret_key, region):
    try:
        password = calculate_key(secret_key, region)
        response = {"status": "success", "data": password}
        return response
    except:
        response = {
            "status": "failed",
            "message": "Whoofps!! error getting SMTP password, debug yourself.",
        }
        return response
