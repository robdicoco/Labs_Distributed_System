from flask import Flask, request, jsonify
import time
import json
import hmac
import hashlib
import secrets

app = Flask(__name__)

SECRET_KEY = b"super_chave_secreta_compartilhada"
NONCES = {}
WINDOW = 30

def canonical_json(data):
    return json.dumps(data, separators=(",", ":"), sort_keys=True)

def cleanup_nonces():
    now = time.time()
    expired = [k for k, v in NONCES.items() if v < now]
    for k in expired:
        del NONCES[k]

def verify_request(req):
    cleanup_nonces()

    timestamp = req.headers.get("X-Timestamp")
    nonce = req.headers.get("X-Nonce")
    signature = req.headers.get("X-Signature")
    body = req.get_json(silent=True) or {}

    if not timestamp or not nonce or not signature:
        return False, "Missing headers"

    try:
        ts = int(timestamp)
    except ValueError:
        return False, "Invalid timestamp"

    if abs(int(time.time()) - ts) > WINDOW:
        return False, "Expired request"

    if nonce in NONCES:
        return False, "Replay detected"

    signing_string = "\n".join([
        req.method.upper(),
        req.path,
        timestamp,
        nonce,
        canonical_json(body)
    ])

    expected = hmac.new(
        SECRET_KEY,
        signing_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return False, "Invalid signature"

    NONCES[nonce] = time.time() + WINDOW
    return True, "OK"

@app.route("/transfer", methods=["POST"])
def transfer():
    ok, msg = verify_request(request)
    if not ok:
        return jsonify({"error": msg}), 401

    data = request.get_json()
    return jsonify({
        "status": "accepted",
        "data": data
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)