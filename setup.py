from setuptools import setup, find_packages

setup(
    name="nexa-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "psutil",
        "cryptography",
        "aiohttp",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "nexa=nexa.interfaces.cli:main",
        ],
    },
)
