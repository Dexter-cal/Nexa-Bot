import json
import os
from pathlib import Path
from cryptography.fernet import Fernet

class SecureConfigStorage:
    """
    Secure storage for API keys and sensitive data
    """

    def __init__(self):
        self.key = self._get_or_create_master_key()
        self.cipher = Fernet(self.key)
        self.config_path = Path.home() / '.nexa' / 'config.enc'

    def _get_or_create_master_key(self):
        """
        Get or create master encryption key
        """

        key_path = Path.home() / '.nexa' / '.key'

        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()

        # Create new key
        key = Fernet.generate_key()

        # Secure the key file
        key_path.parent.mkdir(exist_ok=True, parents=True)
        with open(key_path, 'wb') as f:
            f.write(key)

        # Make it read-only for owner
        os.chmod(key_path, 0o600)

        return key

    async def store_config(self, config: dict):
        """
        Store configuration securely
        """

        # Serialize
        config_json = json.dumps(config)

        # Encrypt
        encrypted = self.cipher.encrypt(config_json.encode())

        # Save
        self.config_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.config_path, 'wb') as f:
            f.write(encrypted)

        # Secure permissions
        os.chmod(self.config_path, 0o600)

    async def load_config(self):
        """
        Load configuration securely
        """

        if not self.config_path.exists():
            return {}

        with open(self.config_path, 'rb') as f:
            encrypted = f.read()

        # Decrypt
        decrypted = self.cipher.decrypt(encrypted)

        # Deserialize
        config = json.loads(decrypted.decode())

        return config
