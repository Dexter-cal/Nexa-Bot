import os
import re
from pathlib import Path
from typing import List, Dict

class DigitalLifeScanner:
    """
    Scan user's digital life for privacy issues
    """
    async def scan_files(self) -> List[Dict]:
        issues = []
        patterns = {
            'api_key': r'api[_-]?key\s*[:=]\s*[\'"]?([a-zA-Z0-9-_]{20,})',
            'password': r'password\s*[:=]\s*[\'"]?([^\s\'"]+)',
            'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
            'private_key': r'-----BEGIN (RSA |)PRIVATE KEY-----'
        }

        # Search in some common directories
        search_paths = [Path.home() / 'Documents', Path.home() / '.nexa']

        for path in search_paths:
            if not path.exists(): continue
            for file in path.rglob('*'):
                if file.is_file() and file.suffix in ['.env', '.config', '.txt', '.log']:
                    try:
                        content = file.read_text(errors='ignore')
                        for name, pattern in patterns.items():
                            if re.search(pattern, content):
                                issues.append({
                                    'type': 'exposed_credential',
                                    'credential_type': name,
                                    'file': str(file)
                                })
                    except:
                        continue

        return issues
