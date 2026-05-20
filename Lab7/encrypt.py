from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

ciphertext = public_key.encrypt(
    b"mensagem secreta",
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)