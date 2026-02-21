from setuptools import setup, find_packages

setup(
    name="epex-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "psutil",
        "cryptography",
        "aiohttp",
        "python-dotenv",
        "python-whois",
    ],
    entry_points={
        "console_scripts": [
            "epex=epex.interfaces.cli:main",
        ],
    },
)
