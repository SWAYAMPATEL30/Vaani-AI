<div align="center">

<img src="assets/banner.png" width="100%" alt="Vaani AI Banner">

# 🎙️ Vaani AI

### *Hindi-Language Conversational Phone AI — Fully Open-Source STT · LLM · TTS Pipeline*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Twilio](https://img.shields.io/badge/Twilio-Webhooks-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper_STT-412991?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/openai/whisper)

<br/>

> **Real phone calls answered by AI — in Hindi — with zero paid STT/TTS costs.**  
> *Vaani* (वाणी) means Voice. Whisper transcribes speech locally → Groq LLaMA generates a Hindi response → Facebook MMS speaks it back directly to the caller.

<br/>

</div>

---

## ⚡ Highlights

*   🛡️ **100% Secure**: No secrets or real keys included in codebase. Sanity-tested pipeline.
*   💰 **Zero Operational Cost**: Uses local models for Speech-to-Text (STT) and Text-to-Speech (TTS). Only paying for API consumption (Groq) which is essentially free/cheap tier!
*   ⚡ **Lightning Fast Async Execution**: Parallel execution threads prevent webhook triggers on synchronous Twilio timeouts.
*   📂 **Dashboard Interface Supported**: Full APIs created to hook into front-facing dashboards easily.

---

## ✨ What It Does

When someone **calls your Twilio number**, this system:

1. 📞 **Answers the call** and plays a smooth Hindi greeting
2. 🎙️ **Listens** to what the caller says (Twilio Gather / Record)
3. 🧠 **Transcribes speech → text** using OpenAI Whisper (runs **100% locally**)
4. 💬 **Generates a contextual Hindi reply** using Groq's LLaMA-3.3-70B (under ~2.5s)
5. 🔊 **Synthesizes the reply to audio** using Facebook MMS TTS hindi (runs **100% locally**)
6. 📢 **Plays the audio back** to the caller via Twilio `<Play>`
7. 🔁 **Loops the conversation** seamlessly until the caller hangs up

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S PHONE                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ Voice Call (PSTN/VoIP)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TWILIO CLOUD                             │
│  ◦ Receives calls          ◦ Records audio                       │
│  ◦ Sends TwiML webhooks    ◦ Plays audio responses               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS Webhooks (TwiML)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               FLASK SERVER (app.py)  ─  Port 5000               │
│  /webhook/incoming  →  /webhook/transcription  →  /webhook/poll  │
│  Async thread pool for STT + LLM + TTS (avoids timeout)         │
└──────┬──────────────┬──────────────┬──────────────┬─────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐  ┌──────────┐  ┌──────────────┐
│  Whisper │   │   Groq   │  │  MMS TTS │  │   SQLite /   │
│   STT    │   │ LLaMA-3  │  │  Hindi   │  │  PostgreSQL  │
│  LOCAL   │   │  Cloud   │  │  LOCAL   │  │   Database   │
└──────────┘   └──────────┘  └──────────┘  └──────────────┘
```

<details>
<summary><b>🔍 Detailed Call Flow (Expand)</b></summary>

```
📞 Incoming Call
    └─▶  /webhook/incoming    →  Play greeting + Start Gather/Record
           │
    🗣️ User speaks
    └─▶  /webhook/transcription  or  /webhook/recording
           │  ┌─────────────────────────────────────────┐
           │  │          Background Thread               │
           │  │  1. Download audio (if Recording path)  │
           │  │  2. Whisper STT → transcript text        │
           │  │  3. Save transcript to DB               │
           │  │  4. Groq LLM → Hindi response text      │
           │  │  5. Save AI response to DB              │
           │  │  6. MMS TTS → .wav audio file           │
           │  │  7. CALL_JOBS[sid] = "ready"            │
           │  └─────────────────────────────────────────┘
           └─▶  Immediately redirect to /webhook/poll
                    └─▶  Twilio polls every 5s
                         └─▶  When "ready" → <Play> audio
                              └─▶  Back to Gather → loop 🔁
```
</details>

---

## 🤖 AI Models & Providers

| Layer | Primary | Alternatives | Cost |
|-------|---------|-------------|------|
| **STT** | Whisper `base` (local) | AssemblyAI, OpenAI Whisper API | **Free** |
| **LLM** | Groq · LLaMA-3.3-70B | Gemini Pro, GPT-4o-mini, Mistral-7B | ~$0.10/1M tokens |
| **TTS** | Facebook MMS TTS `hin` (local) | Veena TTS, ElevenLabs, Google Cloud TTS | **Free** |
| **Telephony** | Twilio | Exotel | Pay-per-minute |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- [Twilio account](https://www.twilio.com/) (free trial works)
- [Groq API key](https://console.groq.com/) (free tier available)
- [ngrok](https://ngrok.com/) for local development

### 1 — Clone & Install

```bash
git clone https://github.com/SWAYAMPATEL30/Vaani-AI.git
cd Vaani-AI

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2 — Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
# Required
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3 — Start Server

```bash
python app.py
```

### 4 — Expose with ngrok

```bash
ngrok http 5000
```

Update your Twilio webhook under **Voice & Fax → A call comes in** → HTTP POST as:
`https://[ngrok-sub].ngrok-free.app/webhook/incoming`

---

## 📁 Project Structure

```
voice/
├── assets/                         # 🖼️ README Banner, Images, media
├── app.py                          # 🚀 Main Flask app — all webhooks & async logic
├── config.py                       # ⚙️ Environment & configuration management
├── models.py                       # 🗄️ SQLAlchemy DB models (Call, CallTranscript)
├── .env.example                    # 🔑 Environment variables template
│
├── services/
│   ├── whisper_local_service.py    # 🎤 OpenAI Whisper STT (local, offline)
│   ├── huggingface_asr_service.py  # 🎧 STT orchestrator (Whisper wrapper)
│   ├── mms_tts_local_service.py    # 🔊 Facebook MMS TTS Hindi (local, offline)
│   ├── tts_service.py              # 🎶 Main TTS router (ElevenLabs/Google/HF)
│   ├── groq_service.py             # 🤖 Groq LLaMA conversation engine
│   └── call_manager.py             # 📞 Twilio call flow management
│
└── [Test Suites, Script Helpers included]
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — all service statuses |
| `POST` | `/webhook/incoming` | Twilio incoming call handler → TwiML response |
| `POST` | `/webhook/transcription` | Twilio text transcription updates |
| `GET/POST` | `/webhook/poll` | Twilio polling endpoint to prevent connection aborts |
| `GET` | `/api/calls` | Get call log traces (SQLite logs) |

---

## 📊 Performance

| Step | Time (CPU) | Time (GPU) |
|------|-----------|-----------|
| Whisper STT | 2–5 sec | < 1 sec |
| Groq LLaMA | 1–3 sec | — (cloud) |
| MMS TTS Hindi | 5–10 sec | < 1 sec |
| **Total pipeline** | **8–18 sec** | **2–4 sec** |

---

## 🚀 Deployment

### Render.com (Recommended)

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://render.com → New Web Service
# 3. Connect your repo, then configure:
#    Build Command: pip install -r requirements.txt
#    Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

For dockerized workflows or AWS deployment details, check [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## 🤝 Contributing

Pull requests are welcome! For major design changes, open an issue first.

1. `feature/amazing-feature` creation
2. Sanity checks run (`python test_all.py`)
3. Open PR log on GitHub!

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ — Vaani AI**

*Bringing AI-powered Hindi conversations to every phone call*

[![GitHub Stars](https://img.shields.io/github/stars/SWAYAMPATEL30/Vaani-AI?style=social)](https://github.com/SWAYAMPATEL30/Vaani-AI)
[![GitHub Forks](https://img.shields.io/github/forks/SWAYAMPATEL30/Vaani-AI?style=social)](https://github.com/SWAYAMPATEL30/Vaani-AI/fork)

</div>
