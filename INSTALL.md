# 🚀 EPEX BOT - ZERO-FRICTION INSTALLATION GUIDE (v5.0 APEX)

Welcome to the future of AI orchestration. Follow these steps to get EPEX running in under 60 seconds.

## 🛠 Prerequisites
- **Python 3.11+**
- **pip** (Python package manager)
- **Ollama** (Optional, for local LLMs)

## ⚡ One-Command Install

```bash
curl -sSL https://get.epex.bot/install.sh | bash
```

## 🚀 EPEX Unified Launcher (epex.py)
The primary entry point for everything is now `epex.py`. It automatically handles environment repair, setup, and interface selection.

```bash
# To install and start for the first time
python epex.py

# To restart EPEX anytime (even after PC shutdown)
python epex.py
```

## 🌍 Global Access (CLI)
During the first setup, EPEX offers to add a global `epex` command to your shell. Once active, you can simply type `epex` from any directory.

If you skipped this, you can manually add it:
```bash
echo "alias epex='python3 $(pwd)/epex.py'" >> ~/.bashrc
source ~/.bashrc
```

### 🛠 Disaster Recovery
If your configuration becomes corrupted or you want a fresh start:
1. Delete the configuration folder: `rm -rf ~/.epex`
2. Rerun the launcher: `python epex.py`

## 🤖 First Run & Configuration

The `epex.py` script will automatically guide you through:
- **Dependency Repair**: Ensures all required libraries are installed.
- **Setup Wizard**:
    - **Password Protection**: Secure your agent with a master password.
    - **Intelligence Providers**: Search & Connect 25+ AI providers.
    - **Connectivity Testing**: Proactive testing for all models before reporting 'Online'.
- **Interface Selection**: Select from **TUI** (adaptive), **GUI** (web dashboard), or **CLI**.

## 🔑 Easy API Key Setup
For a complete list of 25+ supported providers and direct links to get their keys, see [KEYS.md](KEYS.md).

### Quick Commands for Key Management:
```bash
epex --key openai sk-123...
epex --key google AIza...
```
*All keys are encrypted at rest using AES-256 in your local secure vault.*

## 🏠 Local LLM Support (Ollama)
EPEX supports 100% offline execution:
1. Install Ollama from [ollama.com](https://ollama.com).
2. EPEX will automatically detect local models and use them for Tier 4 (unrestricted) or offline tasks.

## 📱 Mobile App Connection
1. Download the EPEX Mobile app.
2. Type `epex tool system.generate_pairing_qr` on your PC.
3. Scan the QR code to sync your **Encrypted Digital Soul**.

---
**EPEX BOT** was created by **Henry Calvin**.
*Neural Orchestration for the Modern Age.*
