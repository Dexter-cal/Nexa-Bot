import asyncio
from typing import List, Dict
import re
import os
from pathlib import Path

class DigitalLifeScanner:
    """
    Scan user's digital life for privacy issues
    """

    def __init__(self):
        self.privacy_issues = []

    async def scan_privacy_issues(self) -> List[Dict]:
        """
        Comprehensive privacy scan
        """
        issues = []
        issues.extend(await self.scan_files())
        issues.extend(await self._scan_clipboard())
        return issues

    async def scan_files(self) -> List[Dict]:
        """
        Scan files for exposed credentials
        """
        issues = []
        patterns = {
            'api_key': r'api[_-]?key\s*[:=]\s*[\'"]?([a-zA-Z0-9-_]{20,})',
            'password': r'password\s*[:=]\s*[\'"]?([^\s\'"]+)',
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'private_key': r'-----BEGIN (RSA |)PRIVATE KEY-----'
        }

        # Scan common locations (limited for safety in this environment)
        scan_dirs = [
            Path.home() / 'Documents',
            Path.home() / '.nexa'
        ]

        for directory in scan_dirs:
            if not directory.exists():
                continue

            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.txt', '.log', '.env', '.config']:
                    try:
                        content = file_path.read_text(errors='ignore')
                        for name, pattern in patterns.items():
                            matches = re.findall(pattern, content)
                            if matches:
                                issues.append({
                                    'type': 'exposed_credential',
                                    'credential_type': name,
                                    'file': str(file_path),
                                    'count': len(matches)
                                })
                    except Exception:
                        continue
        return issues

    async def _scan_clipboard(self) -> List[Dict]:
        """
        Scan clipboard history for sensitive data
        """
        issues = []
        try:
            import pyperclip
            clipboard = pyperclip.paste()

            if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', clipboard):
                issues.append({
                    'type': 'clipboard_leak',
                    'data_type': 'credit_card',
                    'message': 'Credit card number detected in clipboard'
                })
        except ImportError:
            pass # pyperclip not installed
        except Exception:
            pass
        return issues
