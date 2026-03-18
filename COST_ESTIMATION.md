# Cost Estimation Document
## Smart Voice Calling Agent - Per Minute & Overall Costs

---

## 1. Cost Breakdown Per Minute of Call

### Assumptions
- Average call duration: **3 minutes**
- Average turns per call: **3-5 exchanges** (user speaks → AI responds)
- Average user speech: **10 seconds per turn**
- Average AI response: **15 seconds per turn**

---

## 2. Per-Minute Cost Components

### A. Telephony (Twilio) - **$0.013/minute**
- **Service**: Twilio Voice Calls
- **Rate**: $0.013 per minute for calls to/from India
- **Details**: 
  - Inbound calls: $0.013/min
  - Outbound calls: $0.013/min
  - No setup fees
  - Pay-as-you-go pricing
- **Source**: Twilio India pricing (2024)

### B. LLM (Groq API) - **~$0.0001/minute**
- **Service**: Groq Cloud API
- **Model**: `llama-3.3-70b-versatile`
- **Pricing**: 
  - **Free Tier**: 14,400 requests/day (generous free tier)
  - **Paid**: ~$0.10 per 1M input tokens, $0.80 per 1M output tokens
- **Per Call Estimate**:
  - Input tokens: ~200 tokens (user query + context)
  - Output tokens: ~150 tokens (AI response)
  - Cost per turn: ~$0.00002
  - Cost per 3-minute call (5 turns): ~$0.0001
- **Note**: Free tier covers most small-scale usage

### C. STT (Speech-to-Text) - **$0.00/minute** ✅
- **Service**: Local OpenAI Whisper (open-source)
- **Cost**: **FREE** (runs on your hardware)
- **No API calls** - completely offline
- **Alternative**: AssemblyAI ($0.00025/second = $0.015/minute) - **NOT USED**

### D. TTS (Text-to-Speech) - **$0.00/minute** ✅
- **Service**: Local Facebook MMS TTS Hindi (open-source)
- **Cost**: **FREE** (runs on your hardware)
- **No API calls** - completely offline
- **Alternative**: ElevenLabs ($0.30 per 1000 characters) - **NOT USED**

### E. Infrastructure (ngrok) - **$0.00-0.008/minute**
- **Service**: ngrok Public URL Tunneling
- **Free Tier**: 
  - 1 tunnel
  - Dynamic URLs (changes on restart)
  - **FREE** for development
- **Paid Plans**: 
  - Static URLs: $8/month
  - Multiple tunnels: $8-50/month
  - **Per-minute cost**: ~$0.008 (if using paid plan, amortized)

### F. Storage & Database - **~$0.00/minute**
- **SQLite Database**: FREE (local file)
- **Audio Files**: Minimal storage (~50-200 KB per file)
- **Cost**: Negligible for small-scale usage

---

## 3. Total Cost Per Minute

| Component | Cost per Minute | Notes |
|-----------|----------------|-------|
| **Twilio (Telephony)** | $0.013 | Required |
| **Groq LLM** | $0.0001 | Free tier covers most usage |
| **STT (Whisper)** | $0.00 | Local, free |
| **TTS (MMS)** | $0.00 | Local, free |
| **ngrok** | $0.00 | Free tier sufficient |
| **Storage** | $0.00 | Negligible |
| **TOTAL** | **~$0.013/minute** | **~₹1.08/minute** (at ₹83/USD) |

---

## 4. Cost Per Call (3-minute average)

- **Telephony**: $0.013 × 3 = **$0.039** (~₹3.24)
- **LLM**: $0.0001 × 3 = **$0.0003** (~₹0.02)
- **STT/TTS**: **$0.00**
- **Infrastructure**: **$0.00** (free tier)
- **TOTAL PER CALL**: **~$0.039** (**~₹3.24 per call**)

---

## 5. Monthly Cost Estimates

### Scenario 1: Low Volume (100 calls/month)
- **Calls**: 100 × 3 minutes = 300 minutes
- **Twilio**: 300 × $0.013 = **$3.90**
- **Groq**: Covered by free tier = **$0.00**
- **ngrok**: Free tier = **$0.00**
- **TOTAL**: **~$3.90/month** (**~₹324/month**)

### Scenario 2: Medium Volume (1,000 calls/month)
- **Calls**: 1,000 × 3 minutes = 3,000 minutes
- **Twilio**: 3,000 × $0.013 = **$39.00**
- **Groq**: Covered by free tier = **$0.00**
- **ngrok**: Free tier = **$0.00**
- **TOTAL**: **~$39.00/month** (**~₹3,237/month**)

### Scenario 3: High Volume (10,000 calls/month)
- **Calls**: 10,000 × 3 minutes = 30,000 minutes
- **Twilio**: 30,000 × $0.013 = **$390.00**
- **Groq**: May exceed free tier (~$5-10/month) = **~$7.50**
- **ngrok**: Paid plan (static URL) = **$8.00**
- **TOTAL**: **~$405.50/month** (**~₹33,656/month**)

### Scenario 4: Enterprise (100,000 calls/month)
- **Calls**: 100,000 × 3 minutes = 300,000 minutes
- **Twilio**: 300,000 × $0.013 = **$3,900.00**
- **Groq**: ~$75/month (high volume)
- **ngrok**: Enterprise plan = **$50.00**
- **Server Infrastructure**: ~$50-100/month (cloud hosting)
- **TOTAL**: **~$4,075-4,125/month** (**~₹338,225-342,375/month**)

---

## 6. Cost Comparison with Alternatives

### Current Setup (Local STT/TTS)
| Component | Cost |
|-----------|------|
| Twilio | $0.013/min |
| Groq LLM | $0.0001/min (free tier) |
| STT (Local) | $0.00 |
| TTS (Local) | $0.00 |
| **TOTAL** | **~$0.013/min** |

### Alternative: Cloud-Based STT/TTS
| Component | Cost |
|-----------|------|
| Twilio | $0.013/min |
| Groq LLM | $0.0001/min |
| AssemblyAI STT | $0.015/min |
| ElevenLabs TTS | ~$0.05/min |
| **TOTAL** | **~$0.078/min** (**6x more expensive**) |

**Savings with Local STT/TTS**: **~$0.065/minute** (85% cost reduction)

---

## 7. Hidden Costs & Considerations

### Development Costs
- **Time**: Initial setup and configuration
- **Testing**: Twilio test credits (free $15.50 trial)
- **ngrok**: Free tier sufficient for development

### Infrastructure Costs (Production)
- **Cloud Server**: $10-50/month (AWS EC2, DigitalOcean, etc.)
- **Domain Name**: $10-15/year (optional, for static webhook URLs)
- **SSL Certificate**: Free (Let's Encrypt) or $50-100/year

### Scaling Costs
- **Load Balancer**: $20-50/month (for high availability)
- **Database**: PostgreSQL on cloud ($10-50/month for managed DB)
- **CDN**: Optional, for audio file delivery ($5-20/month)

### Maintenance Costs
- **Monitoring**: Free (basic) or $10-50/month (advanced)
- **Backup**: $5-10/month (automated backups)
- **Support**: Internal or external (variable)

---

## 8. Cost Optimization Tips

### 1. Use Free Tiers
- ✅ Groq free tier (14,400 requests/day)
- ✅ ngrok free tier (for development)
- ✅ Local STT/TTS (zero cost)

### 2. Optimize Call Duration
- Keep AI responses concise (reduces call time)
- Use efficient conversation flow (fewer turns)

### 3. Batch Processing
- Process multiple calls on same server (shared resources)
- Use connection pooling for database

### 4. Caching
- Cache common AI responses (if applicable)
- Reuse TTS audio for common phrases

### 5. Server Optimization
- Use GPU for faster TTS/STT (reduces processing time)
- Optimize model sizes (use smaller models if acceptable)

---

## 9. Budget Planning

### Startup Phase (0-100 calls/month)
- **Budget**: $5-10/month
- **Components**: Twilio only (Groq/ngrok free)

### Growth Phase (100-1,000 calls/month)
- **Budget**: $40-50/month
- **Components**: Twilio + optional ngrok paid plan

### Scale Phase (1,000-10,000 calls/month)
- **Budget**: $400-500/month
- **Components**: Twilio + Groq paid + ngrok + server

### Enterprise Phase (10,000+ calls/month)
- **Budget**: $4,000-5,000/month
- **Components**: All services + infrastructure + support

---

## 10. ROI Analysis

### Cost per Call: ~$0.039 (~₹3.24)
### Potential Revenue (Example Use Cases)
- **Customer Support**: $5-20 per call (saved agent time)
- **Lead Qualification**: $10-50 per qualified lead
- **Appointment Booking**: $2-10 per booking
- **Information Service**: $0.50-2 per call (ad revenue, subscriptions)

### Break-Even
- If each call generates **$0.10+ in value**, system is profitable
- Most use cases have **10-100x ROI**

---

## 11. Payment Methods

### Twilio
- Credit card or bank transfer
- Pay-as-you-go (no monthly commitment)
- Billing: Monthly

### Groq
- Credit card
- Free tier, then pay-as-you-go
- Billing: Monthly

### ngrok
- Credit card
- Monthly or annual plans
- Billing: Monthly/annual

---

## 12. Cost Monitoring

### Tools
- **Twilio Console**: Real-time usage and billing
- **Groq Dashboard**: API usage and costs
- **ngrok Dashboard**: Tunnel usage and limits

### Alerts
- Set up billing alerts in Twilio (e.g., $50/month limit)
- Monitor Groq usage to avoid unexpected charges
- Track ngrok tunnel limits (free tier)

---

## 13. Summary

### Key Takeaways
1. **Primary Cost**: Twilio telephony ($0.013/minute)
2. **STT/TTS**: **FREE** (local models)
3. **LLM**: Mostly free (Groq free tier)
4. **Total**: **~$0.013/minute** (~₹1.08/minute)

### Cost Efficiency
- **85% cheaper** than cloud-based STT/TTS alternatives
- **Scalable**: Costs grow linearly with call volume
- **Predictable**: No surprise charges (except Groq if exceeding free tier)

---

**Last Updated**: 2024
**Currency**: USD (converted to INR at ₹83/USD for reference)
**Note**: Prices may vary by region and time. Check official pricing pages for latest rates.
