# 🧠 EPEX BOT: Technical Deep Dive & System Architecture

This document explains the inner workings of EPEX APEX v5.0 and how the 7-layer architecture enables autonomous operation.

---

## 🏗️ The 7-Layer Neural OS

### Layer 1: Foundation (Security & Isolation)
- **Encryption**: All configuration and keys are stored in an AES-256 encrypted vault (`config.enc`).
- **Authentication**: Access is guarded by bcrypt-hashed passwords with 1-hour session persistence.
- **Sandboxing**: High-risk tools are executed within Docker containers or restricted system environments.

### Layer 2: Memory & Data
- **Digital Soul**: A dynamic profile (`soul.json`) that evolves based on user interactions, sentiment, and preferences.
- **Vector Memory**: Uses semantic embeddings to store and retrieve long-term context from past conversations and tasks.
- **Audit Blockchain**: Every command execution is recorded in an immutable local blockchain for forensic accountability.

### Layer 3: Tool Layer
- **Tool Registry**: A central hub managing 180+ specialized tools.
- **Discovery**: Automatically identifies system capabilities and third-party integrations (e.g., Telegram, Discord).
- **Extensibility**: Users can define new tools in natural language, which are then autonomously synthesized and registered.

### Layer 4: Orchestration
- **Task Manager**: Decomposes complex natural language prompts into executable task graphs.
- **Agent Spawner**: Dynamically creates specialized sub-agents (e.g., "Hacker", "Researcher", "Dev") to handle specific subtasks.
- **Swarm Intelligence**: Manages parallel execution across multiple agents to accelerate complex goals.

### Layer 5: Intelligence
- **Enhanced LLM Router**: An intelligent decision engine that selects the best model for a task based on cost, speed, quality, and risk.
- **Model Discovery**: Autonomously scans HuggingFace for trending models, categorizing them (Text, Image, Code, etc.) for human review and approval.
- **Refusal Detection**: Proactively identifies AI refusals and automatically reformulates prompts or switches to unrestricted models.
- **AI Council**: Engages multiple models from different providers to reach a consensus on critical or high-risk decisions.

### Layer 6: User Controls
- **Aegis Filter**: A zero-trust content filter that scrubs outgoing responses for accidentally leaked secrets or keys.
- **Kill Switches**: A tiered system allowing users to stop specific tasks, pause all agents, or perform a full system lockdown.
- **Guardrails**: Text-based rules that define the boundaries of autonomous behavior.

### Layer 7: Interfaces
- **Multi-Modal Access**: Unified backend supporting a raw CLI, an interactive Textual TUI, a modern Web Dashboard, and a Native Desktop Interface (PyQt6).
- **Messaging Hub**: Integrated support for 9+ social platforms including Telegram, Discord, and Slack.
- **Peer Networking**: Distributed neural architecture allowing multi-instance connectivity and task delegation.
- **Neural Sync**: Real-time feedback loop between the engine and the UI, showing "thoughts", latency, and cost in every response.

---

## 🔄 The Execution Lifecycle

1. **Input**: A user submits a command via CLI, TUI, GUI, or a messaging bridge (Telegram).
2. **Analysis**: The `TaskAnalyzer` profiles the prompt for risk, complexity, and required capabilities.
3. **Routing**: The `LLMRouter` selects the optimal model. If it's a complex task, the `HybridExecutor` branches the goal into subtasks.
4. **Execution**: The `TaskManager` runs tools and interacts with models. Sub-agents may be spawned if needed.
5. **Validation**: The result is checked against guardrails and scrubbed by the `Aegis` filter.
6. **Delivery**: The response is delivered to the user with full metadata (cost, tokens, thoughts).
7. **Learning**: The `SoulFile` and `VectorMemory` are updated based on the interaction.

---

## 🛠️ Performance & Scalability

EPEX is designed to handle high-throughput operations with sub-second routing latency and efficient resource management. It supports horizontal scaling through its Instance Network, allowing multiple EPEX nodes to delegate tasks to each other.
