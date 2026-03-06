import asyncio
import subprocess
import sys
import logging
import importlib.util
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class AutonomousToolDiscovery:
    """
    Dynamically discover and install missing tools or libraries
    """

    def __init__(self):
        self.known_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'yaml': 'PyYAML',
            'sklearn': 'scikit-learn',
            'skimage': 'scikit-image',
            'pg8000': 'pg8000',
            'psycopg2': 'psycopg2-binary'
        }
        self.installed_this_session = set()

    async def discover_and_install(self, package_name: str) -> bool:
        """
        Attempt to discover and install a package
        """
        pip_package = self.known_mappings.get(package_name, package_name)

        if pip_package in self.installed_this_session:
            return True

        logger.info(f"🔍 Attempting to discover/install: {pip_package}")

        try:
            # Check if it's already installed but not in current session set
            if self.is_installed(package_name):
                return True

            # Attempt installation
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", pip_package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"✅ Successfully installed {pip_package}")
                self.installed_this_session.add(pip_package)
                # Refresh sys.path or inform user to restart if necessary
                # For most pip installs, importlib.invalidate_caches() helps
                importlib.invalidate_caches()
                return True
            else:
                logger.error(f"❌ Failed to install {pip_package}: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error during tool discovery: {e}")
            return False

    def is_installed(self, package_name: str) -> bool:
        """
        Check if a package is installed
        """
        # Try to find spec
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            return True

        # Try a more thorough check via pip list if needed, but find_spec is usually enough
        return False

    async def find_missing_dependencies(self, code: str) -> List[str]:
        """
        Analyze code to find potentially missing dependencies
        """
        missing = []
        # Very simple regex-less check for imports
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                parts = line.split()
                if len(parts) >= 2:
                    module = parts[1].split('.')[0]
                    if not self.is_installed(module):
                        missing.append(module)
        return list(set(missing))

    async def heal_code_dependencies(self, code: str) -> bool:
        """
        Find and install all missing dependencies for a block of code
        """
        missing = await self.find_missing_dependencies(code)
        if not missing:
            return True

        results = []
        for pkg in missing:
            results.append(await self.discover_and_install(pkg))

        return all(results)
