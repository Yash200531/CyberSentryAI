# CyberSentryAI - Model Configuration & Selection Guide

## 🎯 Selected Production Models

### Summary Table

| Purpose | Model | Speed | Size | Why Selected |
|---------|-------|-------|------|--------------|
| **Red-Team AI** | `HuggingFaceH4/zephyr-7b-beta` | ~2-3s | 7B params | Best instruction-following for reasoning |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 15k/s | 80MB | Optimal speed/quality balance |
| **Text Detection** | `mrm8488/bert-tiny-finetuned-sms-spam-detection` | <1s | Tiny | Production-ready spam detection |
| **Image Detection** | `prithivMLmods/DeepFake-Detection` | 2-3s | Medium | High deepfake accuracy |

---

## 1. Red-Team AI Reasoning

### Selected: `HuggingFaceH4/zephyr-7b-beta`

**Why This Model:**
- ✅ **Instruction-tuned:** Follows complex prompts accurately
- ✅ **Reasoning capability:** Understands attacker psychology
- ✅ **JSON output:** Structured response generation
- ✅ **Production-ready:** Stable API endpoint
- ✅ **Speed:** 2-3s inference (acceptable for analysis)
- ✅ **Context window:** 8K tokens (sufficient for content analysis)

**What It Does:**
- Analyzes attack goals and objectives
- Identifies victim profiles
- Detects psychological manipulation tactics
- Maps exploitation chains
- Predicts next attacker moves

**Alternative Options:**

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `mistralai/Mistral-7B-Instruct-v0.2` | Slower (4-5s) | Higher | When accuracy > speed |
| `google/flan-t5-base` | Faster (1-2s) | Lower | When speed > detail |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Very fast (<1s) | Basic | Low-resource environments |

**Configuration:**
```python
HF_REDTEAM_MODEL=HuggingFaceH4/zephyr-7b-beta
```

---

## 2. Cyber DNA Embeddings

### Selected: `sentence-transformers/all-MiniLM-L6-v2`

**Why This Model:**
- ✅ **Speed:** 15,000 sentences/sec on CPU
- ✅ **Dimensions:** 384 (optimal for similarity)
- ✅ **Size:** 80MB (lightweight)
- ✅ **Quality:** 68% accuracy on STS benchmark
- ✅ **Production-proven:** Millions of downloads
- ✅ **Multilingual:** English-focused, cross-language capable

**What It Does:**
- Generates 384-dimensional semantic embeddings
- Enables cosine similarity matching
- Powers threat lineage detection
- Creates searchable vector representations

**Performance Metrics:**
- **CPU:** 15,000 sentences/sec
- **GPU:** 60,000+ sentences/sec
- **Latency:** ~50ms per embedding
- **Memory:** ~300MB runtime

**Alternative Options:**

| Model | Dimensions | Speed | Size | Use Case |
|-------|------------|-------|------|----------|
| `paraphrase-MiniLM-L3-v2` | 384 | 33k/s | 61MB | Ultra-fast, slightly lower quality |
| `all-mpnet-base-v2` | 768 | 2.8k/s | 420MB | Best quality, slower |
| `all-MiniLM-L12-v2` | 384 | 7.5k/s | 120MB | Balance of speed/quality |

**Configuration:**
```python
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Embedding Pipeline:**
```
Text → Tokenization → Model → 384-dim vector → Normalization → Cosine similarity
```

---

## 3. Text/Email Classification

### Selected: `mrm8488/bert-tiny-finetuned-sms-spam-detection`

**Why This Model:**
- ✅ **Fine-tuned:** Trained specifically on spam/scam data
- ✅ **Fast:** BERT-tiny architecture (<1s inference)
- ✅ **Accurate:** High precision on phishing/scam content
- ✅ **Binary output:** Spam vs Ham classification
- ✅ **API-ready:** Stable HuggingFace endpoint

**What It Does:**
- Classifies text as spam/scam or legitimate
- Returns confidence score (0-1)
- Detects phishing patterns
- Works on SMS, email, messages

**Architecture:**
- Base: BERT-tiny (4 layers, 512 hidden)
- Fine-tuned on: SMS Spam Collection Dataset
- Output: Binary classification + confidence

**Alternative Options:**

| Model | Speed | Use Case |
|-------|-------|----------|
| `distilbert-base-uncased-finetuned-sst-2-english` | Medium | Sentiment + scam detection |
| `cardiffnlp/twitter-roberta-base-sentiment` | Medium | Social media scams |
| `unitary/toxic-bert` | Fast | Toxic content + scams |

**Configuration:**
```python
HF_TEXT_MODEL=mrm8488/bert-tiny-finetuned-sms-spam-detection
```

---

## 4. URL/Phishing Detection

### Current: Using text model for URLs

**Why:**
- URLs are text-based strings
- Same patterns apply (suspicious keywords, obfuscation)
- Text models work well on URL structure

**Future Enhancement:**
Consider specialized URL models:
- `nateraw/bert-base-uncased-emotion` (for emotional manipulation in URLs)
- Custom fine-tuning on PhiUSIIL dataset

**Configuration:**
```python
HF_URL_MODEL=mrm8488/bert-tiny-finetuned-sms-spam-detection
```

---

## 5. Image/Deepfake Detection

### Selected: `prithivMLmods/DeepFake-Detection`

**Why This Model:**
- ✅ **Specialized:** Trained on deepfake datasets
- ✅ **Multi-class:** Detects various manipulation types
- ✅ **API-ready:** Production endpoint available
- ✅ **Accurate:** High precision on synthetic media
- ✅ **Speed:** 2-3s per image (acceptable)

**What It Does:**
- Detects deepfakes and AI-generated faces
- Classifies real vs fake images
- Returns confidence score
- Identifies manipulation artifacts

**Alternative Options:**

| Model | Detection Type | Use Case |
|-------|----------------|----------|
| `dima806/deepfake_vs_real_image_detection` | Deepfake | Alternative high-accuracy |
| `facebook/detr-resnet-50` | Object detection | QR code scams |
| `microsoft/resnet-50` | General vision | Multi-purpose image analysis |

**Configuration:**
```python
HF_IMAGE_MODEL=prithivMLmods/DeepFake-Detection
```

---

## 🔄 Model Switching Guide

### How to Change Models

1. **Update `.env` file:**
```bash
HF_REDTEAM_MODEL=your_new_model_name
```

2. **Restart server:**
```bash
python start.py
```

3. **Test new model:**
```bash
curl -X POST http://localhost:8000/scan/text \
  -H "Content-Type: application/json" \
  -d '{"text": "test content"}'
```

### Model Selection Criteria

When choosing alternative models:

1. **Speed Requirements:**
   - Real-time: <1s inference
   - Interactive: 1-3s inference
   - Batch: >3s acceptable

2. **Accuracy Requirements:**
   - Critical path: 90%+ precision
   - Support features: 70%+ acceptable
   - Experimental: Any quality

3. **Resource Constraints:**
   - CPU-only: Prefer distilled models
   - GPU available: Use larger models
   - Memory limited: Tiny/Mini variants

4. **Cost Considerations:**
   - Free tier: Lightweight models
   - Paid tier: Any model size
   - Self-hosted: Download and run locally

---

## 🚀 Performance Benchmarks

### Latency Targets (per scan)

| Scan Type | Target | Current | Notes |
|-----------|--------|---------|-------|
| Text (simple) | <1s | 1-2s | Primary detection only |
| Text + RedTeam + DNA | <3s | 3-5s | Full analysis pipeline |
| URL (simple) | <1s | 1-2s | Heuristics + API |
| URL + RedTeam + DNA | <3s | 3-5s | Full analysis |
| Image | <2s | 2-4s | HF API + processing |
| Email | <2s | 2-4s | Similar to text |

### Throughput Estimates

With caching and async:
- **Text scans:** 20-30/min
- **Image scans:** 15-20/min
- **Concurrent:** 5-10 simultaneous

---

## 🎛️ Advanced Configuration

### Model Parameters

**Red-Team AI:**
```python
{
    "max_new_tokens": 500,      # Response length
    "temperature": 0.3,          # Creativity (0.3 = focused)
    "top_p": 0.9,               # Nucleus sampling
    "do_sample": True,          # Enable sampling
    "return_full_text": False   # Only new text
}
```

**Embeddings:**
```python
{
    "wait_for_model": True,     # Wait if model loading
    "use_cache": True           # Enable caching
}
```

### Timeout Configuration

Adjust in `.env`:
```bash
HF_TIMEOUT=15  # seconds (default)
```

Recommendations:
- **Development:** 30s (avoid timeouts)
- **Production:** 10-15s (fail fast)
- **High-load:** 5s (aggressive)

---

## 📊 Cost Analysis

### HuggingFace Inference API

**Free Tier:**
- Rate limit: ~30 requests/min
- Suitable for: Development, testing, low-traffic

**Pro Tier ($9/month):**
- Higher rate limits
- Priority queue
- Dedicated endpoints

**Enterprise:**
- Unlimited requests
- SLA guarantees
- Custom endpoints

### Self-Hosting Option

For high volume, consider self-hosting:
```bash
# Download model
from transformers import AutoModel
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Run locally (no API calls)
embeddings = model.encode(["text"])
```

**Pros:**
- No API costs
- Unlimited requests
- Full control

**Cons:**
- Infrastructure costs
- Maintenance overhead
- GPU recommended

---

## 🔮 Future Model Upgrades

### Planned Enhancements

1. **Multi-language Support:**
   - `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   - Detect scams in any language

2. **Voice/Audio Detection:**
   - `facebook/wav2vec2-base-960h`
   - Detect voice phishing (vishing)

3. **OCR Integration:**
   - `microsoft/trocr-base-printed`
   - Extract text from scam images

4. **QR Code Detection:**
   - `facebook/detr-resnet-50`
   - Identify malicious QR codes

---

## 📝 Model Testing Checklist

Before deploying new models:

- [ ] Test on sample data
- [ ] Verify response format
- [ ] Check inference speed
- [ ] Validate accuracy
- [ ] Test error handling
- [ ] Monitor resource usage
- [ ] Document configuration

---

## 🔗 Model Links

### Direct Model URLs

- **Zephyr:** https://huggingface.co/HuggingFaceH4/zephyr-7b-beta
- **MiniLM:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **BERT-tiny:** https://huggingface.co/mrm8488/bert-tiny-finetuned-sms-spam-detection
- **Deepfake:** https://huggingface.co/prithivMLmods/DeepFake-Detection

### Documentation

- **HF Inference API:** https://huggingface.co/docs/api-inference/index
- **Sentence Transformers:** https://www.sbert.net/
- **Model Hub:** https://huggingface.co/models

---

**Last Updated:** January 22, 2026  
**Version:** 2.0.0
