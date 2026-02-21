import os
from cryptography.fernet import Fernet

class PHICryptoManager:
    def __init__(self):
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable is not set.")
        self.cipher_suite = Fernet(key.encode())

    def encrypt_patient_id(self, patient_id: str) -> str:
        """Encrypts a plaintext patient ID into a URL-safe base64-encoded string."""
        if not patient_id:
            return None
        return self.cipher_suite.encrypt(patient_id.encode()).decode()

    def decrypt_patient_id(self, encrypted_patient_id: str) -> str:
        """Decrypts the ciphertext back into the original patient ID."""
        if not encrypted_patient_id:
            return None
        return self.cipher_suite.decrypt(encrypted_patient_id.encode()).decode()

# Instantiate a singleton to use across your ETL scripts
crypto_manager = PHICryptoManager()