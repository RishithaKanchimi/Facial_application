# Generating a key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=20480,
        backend=default_backend()
    )
public_key = private_key.public_key()

# Storing the keys
from cryptography.hazmat.primitives import serialization
pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
with open('private_key.pem', 'wb') as f:
    f.write(pem)
pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
with open('public_key.pem', 'wb') as f:
    f.write(pem)