from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64
import hashlib
import json

class C2Crypto:
    def __init__(self):
        self.rsa_key = None
        self.session_keys = {}  # Store per-agent session keys
        
    def generate_rsa_keypair(self):
        """Generate RSA key pair for server"""
        self.rsa_key = RSA.generate(2048)
        private_key = self.rsa_key.export_key()
        public_key = self.rsa_key.publickey().export_key()
        return private_key, public_key
    
    def decrypt_session_key(self, encrypted_session_key, private_key):
        """Decrypt session key using RSA private key"""
        rsa_key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        session_key = cipher.decrypt(base64.b64decode(encrypted_session_key))
        return session_key
    
    def aes_encrypt(self, data, session_key):
        """AES-256 encryption in GCM mode"""
        cipher = AES.new(session_key, AES.MODE_GCM)
        ciphertext = cipher.encrypt(data.encode() if isinstance(data, str) else data)
        tag = cipher.digest()
        nonce = cipher.nonce
        return base64.b64encode(nonce + ciphertext + tag).decode()
    
    def aes_decrypt(self, encrypted_data, session_key):
        """AES-256 decryption"""
        raw = base64.b64decode(encrypted_data)
        nonce = raw[:16]
        ciphertext = raw[16:-16]
        tag = raw[-16:]
        cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode()
