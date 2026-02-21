# 🚀 EPEX BOT - ZERO-FRICTION INSTALLATION GUIDE (v3.5)

Welcome to the future of AI orchestration. Follow these steps to get Epex Bot running in under 60 seconds.

## 🛠 Prerequisites
- **Python 3.11+**
- **pip** (Python package manager)
- **Ollama** (Optional, for local LLMs)

## ⚡ One-Command Install

```bash
curl -sSL https://get.epex.bot/install.sh | bash
```

## 🚀 EPEX Unified Runner (Recommended)
The simplest way to install and run EPEX is via the unified bootstrap script. It handles dependency management, initial setup, and launching your preferred interface.

```bash
# To install and start for the first time
python epex_run.py

# To restart EPEX anytime
python epex_run.py
```

## 🤖 First Run & Configuration

Simply type:
```bash
epex --setup
```
This will launch the **EPEX APEX v5.0 Setup Wizard**, where you can:
- **Search & Connect Models**: Find any of the 25+ providers or 1000+ Hugging Face models.
- **Test Connections**: Real-time testing for all your API keys (Online/Offline indicators).
- **Choose Interface**: Select your preferred way to interact:
    - **GUI**: High-fidelity web dashboard with drag-and-drop.
    - **TUI**: Lightning-fast terminal interface with Aura-based styling.
    - **CLI**: Raw neural chat for power users.
- **Auto-Launch**: Get taken straight to your chosen interface as soon as setup finishes.

## 🔑 Easy API Key Setup
Setting up your AI models is simple. You can use the CLI, TUI, or the Web Dashboard.

### Full API Key Directory
For a complete list of 25+ supported providers and where to get their keys, see [KEYS.md](KEYS.md).

### Example: Hugging Face (1000+ Models for FREE)
1. Get your token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Run this command:
   ```bash
   epex --key huggingface hf_your_token_here
   ```
3. Done! Epex will now use Hugging Face for research and technical tasks.

### Quick Commands for Other Providers:
```bash
epex --key openai sk-123...
epex --key google AIza...
epex --key anthropic sk-ant...
```
*All keys are encrypted at rest using AES-256 in your local secure vault.*

### Settings via UI
You can also connect keys by navigating to the **Settings** tab in the Web Dashboard or by running the `epex --setup` wizard.

## 🏠 Local LLM Support (Ollama)
Epex supports local execution for 100% privacy:
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull a model: `ollama run llama3.1`
3. Epex will automatically detect Ollama and use it for 'Tier 4' tasks.

## ☁️ Cloud Deployment (Linode)
Deploy Epex as a 24/7 background agent:
1. Spin up a Linode instance (Ubuntu 22.04 LTS).
2. Install Epex using the one-command installer above.
3. Run `epex tool system.linode_deploy` to generate your Docker stack.
4. Access your bot remotely via the **Multi-Instance Network**.

## 🌐 Multi-Instance Network
Connect your bots:
1. On your cloud bot: `epex whoami` to get your API URL and Key.
2. On your laptop: `epex network connect <name> <url> <key>`.
3. Delegation: `epex ask cloud-bot "scan my server health"`.

## 💬 Starting Chat

Once setup is complete, start chatting:
```bash
epex chat
```

## 🚀 EPEX Tool Hub
Browse and launch all 120+ tools through a simple menu system:
```bash
epex --tool-hub
```

## 📱 Mobile App Connection
To connect your phone:
1. Download the Epex Mobile app.
2. Run `epex tool system.generate_pairing_qr` on your main PC.
3. Scan the QR code with your phone to instantly sync memory and tools.

## 🖼 Visual Mockups
To see the architecture in action:
```bash
epex --visuals
```

---
**EPEX BOT** was created by **Henry Calvin**.
*Neural Orchestration for the Modern Age.*

## 👑 About the Creator
**Henry Calvin** is the visionary behind Epex Bot, designing it as a complete autonomous ecosystem for digital maintenance, security, and intelligence orchestration.
