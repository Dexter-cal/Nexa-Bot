# 🔗 CONNECTING NEXA BOT TO YOUR APPS

Nexa Bot can live inside your favorite messaging apps. Follow these simple steps to link them.

---

## 🔹 TELEGRAM (The Best Experience)
Telegram is recommended for Nexa because it supports full bi-directional chat and file sharing.

1. **Create your Bot**:
   - Open Telegram and search for `@BotFather`.
   - Send `/newbot` and follow the instructions to get your **Bot Token**.
2. **Link to Nexa**:
   - Run: `nexa add-key telegram <your_token>`
   - Or run `nexa setup` and select Telegram.
3. **Start Chatting**:
   - Open your new bot in Telegram and type `/start`.
   - You can now send any command or question to Nexa!

---

## 🔹 DISCORD (Team Collaboration)
Use Discord webhooks for notifications or the full Bot API for chat.

### Option A: Webhook (Notifications Only)
1. In your Discord server, go to **Server Settings > Integrations > Webhooks**.
2. Create a new webhook and copy the **Webhook URL**.
3. Link to Nexa: `nexa config set discord_webhook <url>`

### Option B: Bot (Full Chat)
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new Application, then click **Bot**.
3. Copy the **Token**.
4. In Nexa: `nexa add-key discord <token>`

---

## 🔹 WHATSAPP (Mobile Access)
Connecting WhatsApp requires a gateway like Twilio or the Meta WhatsApp Business API.

1. **Get a Twilio Account**:
   - Sign up at [twilio.com](https://twilio.com).
   - Go to the **WhatsApp Sandbox**.
2. **Get your SID and Token**:
   - Copy your `Account SID` and `Auth Token`.
3. **Link to Nexa**:
   - Run: `nexa setup` and choose **WhatsApp/Twilio**.
   - Enter your credentials when prompted.

---

## 🔹 SLACK (Workplace Automation)
1. Go to [api.slack.com/apps](https://api.slack.com/apps).
2. Create a new app "From scratch".
3. Under **OAuth & Permissions**, add `chat:write` and `im:history` scopes.
4. Install the app to your workspace and copy the **Bot User OAuth Token**.
5. Link to Nexa: `nexa add-key slack <token>`

---

## 🔹 SMS (Emergency Alerts)
1. SMS uses the Twilio provider (same as WhatsApp).
2. Once Twilio is linked, you can receive alerts on your phone number.
3. Run: `nexa config set my_phone_number +1234567890`

---

## ⚡ QUICK START TIP
If you have multiple devices, run `nexa visuals` to see how all your instances are coordinating through the **Multi-Instance Network**!

---
**NEXA BOT** — *The Neural OS for the Modern Age.*
Created by **Henry Calvin**.
