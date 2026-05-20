from pqcrypto.kem.ml_kem_512 import generate_keypair, encrypt, decrypt

public_key, secret_key = generate_keypair()

ciphertext, shared_secret_enc = encrypt(public_key)
shared_secret_dec = decrypt(secret_key, ciphertext)

print(shared_secret_enc == shared_secret_dec)
