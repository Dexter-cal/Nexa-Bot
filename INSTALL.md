# 🚀 NEXA BOT - ZERO-FRICTION INSTALLATION GUIDE

Welcome to the future of AI orchestration. Follow these steps to get Nexa Bot running in under 60 seconds.

## 🛠 Prerequisites
- **Python 3.11+**
- **pip** (Python package manager)
- **Virtual Environment** (Recommended)

## ⚡ One-Command Install

```bash
curl -sSL https://get.nexa.bot/install.sh | bash
```

*Or manual installation:*

```bash
# 1. Clone the repository
git clone https://github.com/nexa-bot/nexa.git
cd nexa

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Link the command
pip install -e .
```

## 🤖 First Run

Simply type:
```bash
nexa
```
This will launch the **Interactive Setup Wizard**.

### What happens during setup:
1. **Personalization**: Tell Nexa your name (e.g., "Max") and give your bot a name (e.g., "Bill").
2. **Intelligence Detection**: Nexa analyzes your CPU, RAM, and GPU to recommend the best models.
3. **API Key Discovery**: Nexa automatically scans your environment for existing keys (OpenAI, Google, etc.).
4. **Health Check**: A final validation ensures all 130+ tools are ready.

## 💬 Starting Chat

Once setup is complete, start chatting:
```bash
nexa chat
```

## 🌐 Web Dashboard

To launch the GUI:
```bash
nexa gui
# or
uvicorn nexa.api.main:app --reload
```
Navigate to `http://localhost:8000` to see your agents in action.

---
**NEXA BOT** - *Neural Orchestration for the Modern Age.*
