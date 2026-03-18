# System Requirements Document
## Smart Voice Calling Agent - Hindi AI Assistant

---

## 1. Hardware Requirements

### Minimum Requirements (Development/Testing)
- **CPU**: Intel Core i5 (4th gen) or AMD equivalent (4+ cores)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 20 GB free space (for models and audio files)
- **Network**: Stable internet connection (5+ Mbps)
- **GPU**: Optional but recommended for faster TTS/STT processing
  - NVIDIA GPU with CUDA support (2+ GB VRAM) for faster model inference

### Recommended Requirements (Production)
- **CPU**: Intel Core i7 (8th gen+) or AMD Ryzen 5+ (8+ cores)
- **RAM**: 16 GB minimum, 32 GB recommended
- **Storage**: 50 GB+ SSD (for faster model loading and audio generation)
- **Network**: 10+ Mbps stable connection with low latency
- **GPU**: NVIDIA GPU with 4+ GB VRAM (CUDA 11.8+)
  - Significantly speeds up TTS generation (MMS TTS, Veena TTS)
  - Reduces Whisper STT processing time by 5-10x

### Model Storage Requirements
- **Whisper Model (base)**: ~150 MB
- **MMS TTS Hindi Model**: ~500 MB
- **Veena TTS Model**: ~2 GB (lazy-loaded, optional fallback)
- **Python Packages**: ~5 GB
- **Audio Output**: Variable (depends on call volume)

---

## 2. Software Requirements

### Operating System
- **Windows**: Windows 10/11 (64-bit)
- **Linux**: Ubuntu 20.04+ or Debian 11+ (recommended for production)
- **macOS**: macOS 10.15+ (Catalina or later)

### Python Environment
- **Python**: 3.8, 3.9, 3.10, or 3.11 (3.10+ recommended)
- **pip**: Latest version
- **Virtual Environment**: Recommended (venv, conda, or virtualenv)

### System Dependencies
- **ffmpeg**: Required for audio processing
  - Windows: Download from https://ffmpeg.org/download.html
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
- **CUDA Toolkit** (Optional, for GPU acceleration)
  - Version 11.8+ for NVIDIA GPUs
  - Download from: https://developer.nvidia.com/cuda-downloads

### Development Tools
- **Git**: For version control
- **Code Editor**: VS Code, PyCharm, or any Python IDE
- **Terminal**: PowerShell (Windows), Bash (Linux/macOS)

---

## 3. Python Dependencies

### Core Framework
- `flask==3.0.0` - Web framework for webhooks
- `flask-cors==4.0.0` - CORS support
- `flask-sqlalchemy==3.1.1` - Database ORM
- `sqlalchemy==2.0.23` - Database toolkit
- `python-dotenv==1.0.0` - Environment variable management

### AI/ML Models
- `openai-whisper>=20250625` - Local STT (Speech-to-Text)
- `transformers>=4.30.0` - Hugging Face models (TTS)
- `torch>=2.0.0` - PyTorch (for TTS models)
- `torchaudio>=2.0.0` - Audio processing
- `scipy>=1.10.0` - Scientific computing
- `soundfile>=0.12.0` - Audio file I/O
- `snac>=0.1.0` - Audio codec (for Veena TTS)
- `bitsandbytes>=0.41.0` - Quantization (optional, for GPU memory optimization)

### API Clients
- `groq==0.4.1` - Groq LLM API client
- `twilio==9.0.0` - Twilio telephony SDK
- `requests==2.31.0` - HTTP requests
- `assemblyai==0.28.0` - AssemblyAI STT (optional fallback)
- `openai>=1.12.0` - OpenAI API (optional fallback)
- `google-generativeai==0.3.2` - Google Gemini (optional)

### Audio Processing
- `pydub==0.25.1` - Audio manipulation
- `wave==0.0.2` - WAV file handling

### Utilities
- `python-dateutil==2.8.2` - Date/time utilities
- `uuid==1.30` - UUID generation

### Production Server (Optional)
- `gunicorn==21.2.0` - WSGI server (Linux/macOS)
- `werkzeug==3.0.1` - WSGI utilities

---

## 4. External Services & API Keys

### Required Services
1. **Twilio Account**
   - Account SID
   - Auth Token
   - Phone Number (with voice capabilities)
   - Sign up: https://www.twilio.com/try-twilio

2. **Groq API Key** (Primary LLM)
   - Free tier available
   - Sign up: https://console.groq.com/
   - Model: `llama-3.3-70b-versatile`

3. **ngrok Account** (For local development)
   - Free tier: 1 tunnel, dynamic URLs
   - Paid plans: Static URLs, multiple tunnels
   - Sign up: https://ngrok.com/

### Optional Services (Fallbacks)
- **AssemblyAI API Key** (STT fallback)
- **OpenAI API Key** (LLM/STT fallback)
- **Google Gemini API Key** (LLM alternative)
- **Hugging Face Token** (for private models, if needed)

---

## 5. Network Requirements

### Ports
- **Port 5000**: Flask development server (default)
- **Port 4040**: ngrok web interface (optional)
- **Outbound HTTPS**: For API calls (Twilio, Groq, etc.)

### Firewall
- Allow inbound connections on port 5000 (or configured port)
- Allow outbound HTTPS (443) for API calls
- ngrok handles public URL tunneling automatically

### Bandwidth
- **Minimum**: 5 Mbps (for webhooks and audio streaming)
- **Recommended**: 10+ Mbps (for faster audio download/upload)
- **Latency**: < 100ms to Twilio servers (for real-time calls)

---

## 6. Database Requirements

### Default: SQLite (Local)
- **File**: `instance/voice_agent.db`
- **Storage**: Minimal (~1 MB per 1000 calls)
- **No setup required** - Created automatically

### Optional: PostgreSQL (Production)
- **Version**: PostgreSQL 12+
- **Storage**: Variable (depends on call volume)
- **Connection**: Configure `DATABASE_URL` in `.env`

---

## 7. Storage Requirements

### Audio Files
- **Location**: `audio_output/` directory
- **Format**: WAV files (16-bit, 16kHz or 24kHz)
- **Size per file**: ~50-200 KB (depending on duration)
- **Retention**: Configure cleanup policy (optional)

### Model Cache
- **Hugging Face Cache**: `~/.cache/huggingface/` (default)
- **Whisper Models**: Downloaded on first use
- **TTS Models**: Downloaded on first use

---

## 8. Performance Requirements

### Response Times (Target)
- **STT (Whisper)**: 2-5 seconds per audio clip (CPU), <1 second (GPU)
- **LLM (Groq)**: 1-3 seconds per response
- **TTS (MMS)**: 1-3 seconds per response (CPU), <1 second (GPU)
- **Total Pipeline**: 6-12 seconds per turn (CPU), 3-5 seconds (GPU)

### Concurrent Calls
- **Development**: 1-2 concurrent calls
- **Production**: 5-10 concurrent calls (single server)
- **Scaling**: Use load balancer + multiple servers for higher volume

---

## 9. Security Requirements

### Environment Variables
- Store all API keys in `.env` file (never commit to Git)
- Use `.gitignore` to exclude `.env` from version control
- Rotate API keys regularly

### Webhook Security
- Validate Twilio webhook signatures (optional but recommended)
- Use HTTPS for all webhook endpoints (via ngrok or production server)
- Implement rate limiting for webhook endpoints

### Database Security
- Use strong database passwords (if using PostgreSQL)
- Encrypt sensitive call data (optional, for compliance)

---

## 10. Monitoring & Logging

### Logging
- **Level**: INFO (default), DEBUG (for troubleshooting)
- **Format**: Structured logging with timestamps
- **Location**: Console output (stdout)

### Health Checks
- **Endpoint**: `/health` (returns service status)
- **Monitoring**: Use external monitoring tools (optional)

---

## 11. Installation Checklist

- [ ] Install Python 3.10+
- [ ] Install ffmpeg
- [ ] Install CUDA Toolkit (optional, for GPU)
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install Python dependencies (`pip install -r requirements.txt`)
- [ ] Create `.env` file with API keys
- [ ] Download models (automatic on first use)
- [ ] Test local STT/TTS (`python local_demo.py`)
- [ ] Set up ngrok tunnel
- [ ] Configure Twilio webhook URLs
- [ ] Test end-to-end call flow

---

## 12. Troubleshooting

### Common Issues
1. **Model download fails**: Check internet connection, Hugging Face token
2. **CUDA errors**: Verify CUDA installation, GPU drivers
3. **Port already in use**: Change `PORT` in `.env` or kill existing process
4. **ngrok tunnel fails**: Check ngrok authentication, restart ngrok
5. **Twilio webhook timeout**: Ensure async processing is working, check logs

---

## 13. Production Deployment Considerations

### Server Options
- **Cloud**: AWS EC2, Google Cloud Compute, Azure VM
- **VPS**: DigitalOcean, Linode, Vultr
- **Container**: Docker + Kubernetes (for scaling)

### Recommended Setup
- **OS**: Ubuntu 22.04 LTS
- **Server**: Gunicorn + Nginx (reverse proxy)
- **Process Manager**: systemd or supervisor
- **Monitoring**: Prometheus + Grafana (optional)
- **Backup**: Automated database backups

---

## 14. Support & Documentation

- **README.md**: Quick start guide
- **TROUBLESHOOTING.md**: Common issues and solutions
- **API Documentation**: Inline code comments
- **Logs**: Check terminal output for detailed error messages

---

**Last Updated**: 2024
**Version**: 1.0
