import os
import json
import logging
from pathlib import Path
from epex.foundation.storage import SecureConfigStorage

logger = logging.getLogger(__name__)

class ProfileManager:
    """
    Multiple profiles for different use cases
    """

    def __init__(self):
        self.storage = SecureConfigStorage()
        self.profiles_dir = Path.home() / '.epex' / 'profiles'
        self.profiles_dir.mkdir(exist_ok=True, parents=True)

    async def list_profiles(self):
        return [p.stem for p in self.profiles_dir.glob('*.enc')]

    async def create_profile(self, name: str):
        """
        Create a new profile
        """
        profile_path = self.profiles_dir / f'{name}.enc'
        if profile_path.exists():
            raise ValueError(f"Profile '{name}' already exists")

        # Start with current config or default
        config = await self.storage.load_config()

        # We need a way to store to a specific path in SecureConfigStorage
        # For now, let's just manually handle the encryption here for simplicity
        # or better, update SecureConfigStorage to support paths.

        # Temporarily swap config_path
        old_path = self.storage.config_path
        self.storage.config_path = profile_path
        await self.storage.store_config(config)
        self.storage.config_path = old_path

        return True

    async def switch_profile(self, name: str):
        """
        Switch to different profile
        """
        profile_path = self.profiles_dir / f'{name}.enc'
        if not profile_path.exists():
            raise ValueError(f"Profile '{name}' not found")

        # Load profile
        old_path = self.storage.config_path
        self.storage.config_path = profile_path
        config = await self.storage.load_config()
        self.storage.config_path = old_path

        # Apply to main config
        await self.storage.store_config(config)
        return True
