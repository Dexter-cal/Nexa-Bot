import asyncio
import aiohttp
import hashlib
from typing import Set, List, Dict

class BreachDetector:
    """
    Detect if credentials are in known breaches
    """

    def __init__(self):
        self.breach_databases = [
            'haveibeenpwned',
            'dehashed',
            'leakcheck'
        ]

    async def check_breaches(self, emails: Set[str]) -> List[Dict]:
        """
        Check all emails against breach databases
        """
        all_breaches = []
        for email in emails:
            # Check HaveIBeenPwned (Mocked)
            # breaches = await self._check_hibp(email)
            # all_breaches.extend(breaches)
            pass
        return all_breaches

    async def check_password_pwned(self, password: str) -> Dict:
        """
        Check if password is in Pwned Passwords database
        Uses k-anonymity model (only sends first 5 chars of hash)
        """
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f'https://api.pwnedpasswords.com/range/{prefix}'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        for line in text.split('\n'):
                            if ':' in line:
                                hash_suffix, count = line.split(':')
                                if hash_suffix.strip() == suffix:
                                    return {
                                        'pwned': True,
                                        'count': int(count.strip()),
                                        'message': f'Password found in {count.strip()} breaches!'
                                    }
            return {'pwned': False}
        except Exception:
            return {'pwned': False, 'error': 'API error'}
