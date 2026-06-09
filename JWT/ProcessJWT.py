import base64
import hmac
import hashlib
import json
import time

# The JWT from your PHP login
jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTczMjc3MDEsImV4cCI6MTc1NzMzMTMwMSwidWlkIjo4LCJ1c2VybmFtZSI6IkhpbGQifQ.xfzofF3nmjNeBxnzMcdo2SoTW4ISErwk8nRdoe3W91Q"

# Your secret key (must match the one used in PHP)
secret_key = b"mySuperSecretKey123!"  # bytes

def base64url_decode(input_str):
    rem = len(input_str) % 4
    if rem:
        input_str += '=' * (4 - rem)
    return base64.urlsafe_b64decode(input_str)

def verify_jwt(token, secret):
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
    except ValueError:
        raise ValueError("Invalid JWT format")

    # Decode payload
    payload_json = base64url_decode(payload_b64)
    payload = json.loads(payload_json)

    # Verify signature
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    signature = base64url_decode(signature_b64)

    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")

    # Check expiration
    if "exp" in payload and time.time() > payload["exp"]:
        raise ValueError("Token expired")

    return payload

# Usage
try:
    decoded_payload = verify_jwt(jwt_token, secret_key)
    print("JWT is valid!")
    print("Payload:", decoded_payload)
except Exception as e:
    print("JWT verification failed:", e)
