import time
import json
import hmac
import hashlib
import secrets

SECRET_KEY = b"super_chave_secreta_compartilhada"

def canonical_json(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=True)

def sign_request(method: str, path: str, body: dict) -> dict:
    timestamp = str(int(time.time()))
    nonce = secrets.token_hex(16)

    payload = {
        "timestamp": timestamp,
        "nonce": nonce,
        "body": body
    }

    signing_string = "\n".join([
        method.upper(),
        path,
        timestamp,
        nonce,
        canonical_json(body)
    ])

    signature = hmac.new(
        SECRET_KEY,
        signing_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "headers": {
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Signature": signature,
            "Content-Type": "application/json"
        },
        "body": body
    }

if __name__ == "__main__":
    req = sign_request(
        method="POST",
        path="/transfer",
        body={
            "from_account": "123",
            "to_account": "456",
            "amount": 100.00
        }
    )

    print("Headers:")
    print(json.dumps(req["headers"], indent=2))
    print("Body:")
    print(json.dumps(req["body"], indent=2))