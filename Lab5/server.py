import time
import json
import hmac
import hashlib
from threading import Lock

SECRET_KEY = b"super_chave_secreta_compartilhada"
ALLOWED_CLOCK_SKEW_SECONDS = 30

class NonceStore:
    def __init__(self):
        self.used_nonces = {}
        self.lock = Lock()

    def _cleanup(self):
        now = time.time()
        expired = [nonce for nonce, exp in self.used_nonces.items() if exp < now]
        for nonce in expired:
            del self.used_nonces[nonce]

    def check_and_store(self, nonce: str, ttl_seconds: int) -> bool:
        with self.lock:
            self._cleanup()
            if nonce in self.used_nonces:
                return False
            self.used_nonces[nonce] = time.time() + ttl_seconds
            return True

nonce_store = NonceStore()

def canonical_json(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=True)

def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)

def verify_request(method: str, path: str, headers: dict, body: dict) -> tuple[bool, str]:
    timestamp = headers.get("X-Timestamp")
    nonce = headers.get("X-Nonce")
    signature = headers.get("X-Signature")

    if not timestamp or not nonce or not signature:
        return False, "Cabeçalhos obrigatórios ausentes"

    try:
        ts = int(timestamp)
    except ValueError:
        return False, "Timestamp inválido"

    now = int(time.time())
    if abs(now - ts) > ALLOWED_CLOCK_SKEW_SECONDS:
        return False, "Requisição expirada ou fora da janela permitida"

    if not nonce_store.check_and_store(nonce, ttl_seconds=ALLOWED_CLOCK_SKEW_SECONDS):
        return False, "Replay detectado: nonce já utilizado"

    signing_string = "\n".join([
        method.upper(),
        path,
        timestamp,
        nonce,
        canonical_json(body)
    ])

    expected_signature = hmac.new(
        SECRET_KEY,
        signing_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not constant_time_equal(signature, expected_signature):
        return False, "Assinatura inválida"

    return True, "OK"

if __name__ == "__main__":
    # Simulação de uma requisição recebida
    request_headers = {
        "X-Timestamp": str(int(time.time())),
        "X-Nonce": "abc123nonceunico",
        "X-Signature": ""
    }
    request_body = {
        "from_account": "123",
        "to_account": "456",
        "amount": 100.0
    }

    signing_string = "\n".join([
        "POST",
        "/transfer",
        request_headers["X-Timestamp"],
        request_headers["X-Nonce"],
        canonical_json(request_body)
    ])

    request_headers["X-Signature"] = hmac.new(
        SECRET_KEY,
        signing_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    ok, msg = verify_request("POST", "/transfer", request_headers, request_body)
    print(ok, msg)

    # Replay da mesma requisição
    ok, msg = verify_request("POST", "/transfer", request_headers, request_body)
    print(ok, msg)