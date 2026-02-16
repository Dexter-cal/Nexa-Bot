import aiohttp
import hashlib
from typing import Dict, List, Set

class BreachDetector:
    """
    Detect if credentials are in known breaches
    """
    async def check_password_pwned(self, password: str) -> Dict:
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f'https://api.pwnedpasswords.com/range/{prefix}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    for line in text.split('\n'):
                        if ':' in line:
                            hash_suffix, count = line.split(':')
                            if hash_suffix == suffix:
                                return {'pwned': True, 'count': int(count)}
                return {'pwned': False}
