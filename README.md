# ⚡ EPEX APEX v5.0: The Neural Command Center

**"From Zero to Running in 60 Seconds"**

EPEX is an advanced AI agent orchestration system designed for high-fidelity automation, security research, and autonomous digital operations. Built on a modular 7-layer architecture, it provides a seamless bridge between human intent and complex technical execution.

---

## 🚀 Key Features

- **Multi-Interface Hub**: Switch between high-fidelity CLI, interactive TUI (`textual`), and a modern GUI dashboard (`fastapi`) with a single command.
- **Intelligent Routing**: Advanced model switching across 25+ providers (OpenAI, Anthropic, Google, HuggingFace, Cerebras, SambaNova, etc.).
- **7-Layer Architecture**: Robust separation of concerns from foundation security to human-facing interfaces.
- **Autonomous Swarms**: Spawn and manage specialized agent swarms for parallel task execution.
- **Privacy Guardian**: Real-time breach detection, dark web monitoring, and secret redaction.
- **Self-Healing Engine**: Proactive diagnostic and repair tools for both system and software issues.
- **Neural Memory**: Persistent vector memory with semantic search and cross-session context retention.

---

## 🛠️ Installation

```bash
# One-line installation
curl -sSL https://get.epex.bot | bash

# Manual installation
git clone https://github.com/epex-bot/epex.git
cd epex
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python epex.py
```

---

## 📖 How it Works: The 7-Layer Neural OS

EPEX is organized into seven distinct layers, each handling a critical part of the AI's life-cycle:

1. **Layer 1: FOUNDATION** (Security, Auth, Sandboxing)
   - Secure AES-256 Vault, PBKDF2 Password protection, Docker isolation.
2. **Layer 2: MEMORY & DATA** (Soul, Vector DB, Blockchain)
   - Persistent persona context (Soul File), immutable action logs (Blockchain).
3. **Layer 3: TOOL LAYER** (180+ Tools, Hardware Control)
   - Specialized tools for DevOps, Security, multimedia, and system management.
4. **Layer 4: ORCHESTRATION** (Task Manager, Swarm, Spawner)
   - Decomposes goals into subtasks and delegates to specialized agent swarms.
5. **Layer 5: INTELLIGENCE** (Model Router, AI Council, Macros)
   - Intelligent model selection, refusal prediction, and consensus systems.
6. **Layer 6: USER CONTROLS** (Guardrails, Persona, Kill-Switch)
   - Fine-grained control over AI behavior, risk limits, and emergency stops.
7. **Layer 7: INTERFACES** (CLI, TUI, GUI, API, Voice)
   - Unified access through beautiful, responsive, and functional interfaces.

---

## 🖥️ Command Center Shortcuts

- `epex`: Launch the unified Command Center launcher.
- `epex --tui`: Direct launch into the Textual-based Dashboard.
- `epex --gui`: Launch the FastAPI-based Web Dashboard.
- `epex --cli`: Launch the raw Neural Chat loop.
- `Ctrl+K`: Open the Command Palette (GUI).
- `F1-F4`: Switch tabs in the TUI.

---

## 🛡️ Security First

EPEX implements a **Aegis Zero-Trust Filter** that proactively redacts sensitive information (API keys, passwords) from AI responses. It also includes a **Level 4 Kill Switch** for immediate emergency shutdowns.

---

## ⚖️ License

Created by **Henry Calvin**. Released under the EPEX Advanced License. See `LICENSE` for details.
