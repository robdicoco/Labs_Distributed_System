from pqcrypto.kem.ml_kem_512 import generate_keypair, encrypt, decrypt

# 1. Gerar par de chaves
public_key, secret_key = generate_keypair()

# 2. Encapsular (lado cliente)
ciphertext, shared_secret_enc = encrypt(public_key)

# 3. Decapsular (lado servidor)
shared_secret_dec = decrypt(secret_key, ciphertext)

# 4. Validar
print("Segredo compartilhado (encrypt):", shared_secret_enc)
print("Segredo compartilhado (decrypt):", shared_secret_dec)

print("Match:", shared_secret_enc == shared_secret_dec)