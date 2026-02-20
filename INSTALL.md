# 🚀 NEXA BOT - ZERO-FRICTION INSTALLATION GUIDE (v3.5)

Welcome to the future of AI orchestration. Follow these steps to get Nexa Bot running in under 60 seconds.

## 🛠 Prerequisites
- **Python 3.11+**
- **pip** (Python package manager)
- **Ollama** (Optional, for local LLMs)

## ⚡ One-Command Install

```bash
curl -sSL https://get.nexa.bot/install.sh | bash
```

## 🚀 Nexa Auto-Runner (Bootstrap)
The simplest way to start: just run the bootstrap script.
```bash
python nexa_run.py
```
This will automatically install all dependencies and launch the **Express Setup Wizard**.

## 🤖 First Run

Simply type:
```bash
nexa
```
This will launch the **Interactive Setup Wizard**.

## 🔑 Easy API Key Setup
Setting up your AI models is simple. You can use the CLI, TUI, or the Web Dashboard.

### Full API Key Directory
For a complete list of 25+ supported providers and where to get their keys, see [KEYS.md](KEYS.md).

### Example: Hugging Face (1000+ Models for FREE)
1. Get your token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Run this command:
   ```bash
   nexa --key huggingface hf_your_token_here
   ```
3. Done! Nexa will now use Hugging Face for research and technical tasks.

### Quick Commands for Other Providers:
```bash
nexa --key openai sk-123...
nexa --key google AIza...
nexa --key anthropic sk-ant...
```
*All keys are encrypted at rest using AES-256 in your local secure vault.*

### Settings via UI
You can also connect keys by navigating to the **Settings** tab in the Web Dashboard or by running the `nexa --setup` wizard.

## 🏠 Local LLM Support (Ollama)
Nexa supports local execution for 100% privacy:
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull a model: `ollama run llama3.1`
3. Nexa will automatically detect Ollama and use it for 'Tier 4' tasks.

## ☁️ Cloud Deployment (Linode)
Deploy Nexa as a 24/7 background agent:
1. Spin up a Linode instance (Ubuntu 22.04 LTS).
2. Install Nexa using the one-command installer above.
3. Run `nexa tool system.linode_deploy` to generate your Docker stack.
4. Access your bot remotely via the **Multi-Instance Network**.

## 🌐 Multi-Instance Network
Connect your bots:
1. On your cloud bot: `nexa whoami` to get your API URL and Key.
2. On your laptop: `nexa network connect <name> <url> <key>`.
3. Delegation: `nexa ask cloud-bot "scan my server health"`.

## 💬 Starting Chat

Once setup is complete, start chatting:
```bash
nexa chat
```

## 📱 Mobile App Connection
To connect your phone:
1. Download the Nexa Mobile app.
2. Run `nexa tool system.generate_pairing_qr` on your main PC.
3. Scan the QR code with your phone to instantly sync memory and tools.

## 🖼 Visual Mockups
To see the architecture in action:
```bash
nexa --visuals
```

---
**NEXA BOT** was created by **Henry Calvin**.
*Neural Orchestration for the Modern Age.*

## 👑 About the Creator
**Henry Calvin** is the visionary behind Nexa Bot, designing it as a complete autonomous ecosystem for digital maintenance, security, and intelligence orchestration.
