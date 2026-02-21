import pytest
import os
from cryptography.fernet import Fernet, InvalidToken

# This prevents pytest collection from crashing when etl.security initializes its singleton.
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

# Now it is safe to import the module!
from etl.security import PHICryptoManager, crypto_manager

# ---------------------------------------------------------
# Test Suite for PHI Cryptography & Security (REQ-SEC-01)
# ---------------------------------------------------------

def test_phi_crypto_manager_singleton():
    """Ensure the module-level singleton instantiated correctly from the injected env var."""
    assert crypto_manager is not None
    assert crypto_manager.cipher_suite is not None

def test_phi_crypto_manager_init_missing_key(monkeypatch):
    """Ensure the class hard-crashes if the encryption key is missing during initialization."""
    # Use monkeypatch to temporarily remove the key we injected above
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    
    with pytest.raises(ValueError, match="ENCRYPTION_KEY environment variable is not set."):
        PHICryptoManager()

def test_encrypt_decrypt_patient_id_success():
    """Ensure the cipher completely obscures the text and can be reversed."""
    manager = PHICryptoManager()
    plaintext_id = "PATIENT-XYZ-999"
    
    # 1. Test Encryption
    encrypted_id = manager.encrypt_patient_id(plaintext_id)
    assert encrypted_id is not None
    assert encrypted_id != plaintext_id
    assert "PATIENT" not in encrypted_id  # Ensure no plaintext leakage
    
    # 2. Test Decryption
    decrypted_id = manager.decrypt_patient_id(encrypted_id)
    assert decrypted_id == plaintext_id

def test_encrypt_patient_id_handles_empty_values():
    """Ensure None and empty strings are handled gracefully without crashing."""
    manager = PHICryptoManager()
    assert manager.encrypt_patient_id(None) is None
    assert manager.encrypt_patient_id("") is None

def test_decrypt_patient_id_handles_empty_values():
    """Ensure None and empty strings are handled gracefully without crashing."""
    manager = PHICryptoManager()
    assert manager.decrypt_patient_id(None) is None
    assert manager.decrypt_patient_id("") is None

def test_decrypt_patient_id_invalid_token():
    """Ensure decryption fails securely if the ciphertext is tampered with."""
    manager = PHICryptoManager()
    
    # Fernet raises an InvalidToken exception if the payload is corrupted
    with pytest.raises(InvalidToken):
        manager.decrypt_patient_id("malicious_or_corrupted_ciphertext_here")