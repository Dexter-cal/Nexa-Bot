# 🔑 EPEX UNIVERSAL API KEY DIRECTORY

Epex Bot supports over 25+ AI providers. Use this directory to quickly find where to get your keys and understand the costs.

## 🚀 Recommended for Beginners (Generous FREE Tiers)

| Provider | Why? | Get Key Here |
| :--- | :--- | :--- |
| **Google AI Studio** | 60 RPM Free (Gemini 1.5) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Groq** | Blazing fast, high rate limits | [console.groq.com](https://console.groq.com/keys) |
| **Hugging Face** | 1,000s of open-source models | [huggingface.co](https://huggingface.co/settings/tokens) |
| **Together AI** | $25 free credit for open models | [together.ai](https://api.together.xyz/settings/api-keys) |
| **Jina AI** | 1M free tokens for embeddings | [jina.ai](https://jina.ai/embeddings/) |

## 🏢 Professional & Enterprise LLMs

| Provider | Best For | Get Key Here |
| :--- | :--- | :--- |
| **OpenAI** | GPT-4o, DALL-E 3 | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Anthropic** | Claude 3.5 Sonnet (Logic/Coding) | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| **DeepSeek** | High performance, low cost | [deepseek.com](https://platform.deepseek.com/api_keys) |
| **Mistral AI** | European champion, open weights | [console.mistral.ai](https://console.mistral.ai/api-keys) |
| **xAI (Grok)** | Real-time info from X | [console.x.ai](https://console.x.ai/) |

## 🛠️ Specialized Services

| Provider | Purpose | Get Key Here |
| :--- | :--- | :--- |
| **OpenRouter** | One API for ALL models | [openrouter.ai](https://openrouter.ai/keys) |
| **Perplexity** | Real-time web search/answers | [perplexity.ai](https://www.perplexity.ai/settings/api) |
| **Replicate** | Stable Diffusion, specialized AI | [replicate.com](https://replicate.com/account/api-tokens) |
| **Voyage AI** | Best-in-class RAG embeddings | [voyageai.com](https://dashboard.voyageai.com/) |
| **Novita AI** | Image generation & fast inference | [novita.ai](https://novita.ai/settings/key) |

## 📟 Communication Channels

| Provider | Purpose | Get Key Here |
| :--- | :--- | :--- |
| **Telegram** | Run Epex as a Telegram Bot | [@BotFather](https://t.me/BotFather) |
| **Twilio** | SMS and Voice calling | [twilio.com](https://www.twilio.com/console) |

---

## ⚡ How to Add Keys to Epex

### Option 1: CLI (Fastest)
```bash
epex --key openai sk-...
```

### Option 2: Setup Wizard
```bash
epex --setup
```

### Option 3: Web Dashboard
Open the Epex Web UI and navigate to the **Settings** tab.

### Option 4: Environment Variables
Export keys in your shell:
```bash
export OPENAI_API_KEY='sk-...'
```

---
**Security Note:** All keys are encrypted using AES-256 and stored locally in your `~/.epex/config.enc`. We never see or store your keys on our servers.
