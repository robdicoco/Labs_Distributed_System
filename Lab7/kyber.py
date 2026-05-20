from pqcrypto.kem.ml_kem_512 import generate_keypair, encrypt, decrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# =========================
# 1. Servidor gera chaves Kyber
# =========================
server_public_key, server_secret_key = generate_keypair()

# =========================
# 2. Cliente encapsula uma chave usando a chave pública do servidor
# =========================
kyber_ciphertext, shared_secret_client = encrypt(server_public_key)

# =========================
# 3. Servidor decapsula e obtém o mesmo segredo
# =========================
shared_secret_server = decrypt(server_secret_key, kyber_ciphertext)

print("Segredos iguais?", shared_secret_client == shared_secret_server)

# =========================
# 4. Usa o segredo Kyber como chave AES
# =========================
aes_key_client = shared_secret_client[:32]
aes_key_server = shared_secret_server[:32]

# =========================
# 5. Cliente criptografa mensagem com AES-GCM
# =========================
message = b"Mensagem segura usando Kyber + AES-GCM"

nonce = os.urandom(12)
aes_client = AESGCM(aes_key_client)

encrypted_message = aes_client.encrypt(
    nonce,
    message,
    None
)

print("Mensagem criptografada:", encrypted_message.hex())

# =========================
# 6. Servidor descriptografa mensagem com AES-GCM
# =========================
aes_server = AESGCM(aes_key_server)

decrypted_message = aes_server.decrypt(
    nonce,
    encrypted_message,
    None
)

print("Mensagem descriptografada:", decrypted_message.decode())