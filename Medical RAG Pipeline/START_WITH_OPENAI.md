# 🚀 Start Medical RAG with OpenAI

## ⚡ Quick Start (3 Steps)

### 1️⃣ Install Dependencies
```bash
cd "Medical RAG Pipeline"
pip install openai langchain-openai
```

### 2️⃣ Rebuild Index
```bash
python ingest.py
```
⏱️ Takes 2-5 minutes. Requires internet connection.

### 3️⃣ Start Server
```bash
python api_server.py
```
🌐 Server runs on http://localhost:8000

---

## ✅ What's Different?

| Feature | Before (Ollama) | After (OpenAI) |
|---------|----------------|----------------|
| **LLM Model** | Mistral 7B (local) | GPT-4o-mini (cloud) |
| **Embeddings** | nomic-embed-text | text-embedding-3-small |
| **Setup** | Need to run `ollama serve` | Just API key |
| **Hardware** | GPU recommended | Any machine |
| **Cost** | Free | ~$0.001 per request |
| **Quality** | Good | Better |
| **Speed** | Fast (after loading) | Very fast |

---

## 💰 Cost Estimate

- **Per request**: $0.001-0.002 (0.1-0.2 cents)
- **100 requests**: $0.10-0.20
- **1,000 requests**: $1-2
- **10,000 requests**: $10-20

**Monthly (1000 req/day)**: ~$30-60

Very affordable for production! 🎉

---

## 🔑 API Key

You need to add your OpenAI API key to `config.py`:

1. Get your API key from https://platform.openai.com/api-keys
2. Open `config.py`
3. Replace `"your-openai-api-key-here"` with your actual key

Monitor usage: https://platform.openai.com/usage

---

## 🧪 Test It

### Test with curl:
```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -d @../Backend/test-request.json
```

### Test with Spring Boot:
Your Spring Boot backend at `http://localhost:8080` will automatically use the new OpenAI-powered FastAPI server. No changes needed!

---

## 📊 What Happens Now?

When you call `/assess-structured`:

1. **Spring Boot** sends patient data → **FastAPI** (port 8000)
2. **FastAPI** extracts clinical features
3. **OpenAI Embeddings** convert query to vector
4. **FAISS** retrieves relevant medical guidelines
5. **OpenAI GPT-4o-mini** generates risk assessment
6. **FastAPI** returns structured response → **Spring Boot**
7. **Spring Boot** saves to PostgreSQL

All powered by OpenAI! ☁️

---

## 🎯 Benefits

✅ **No local setup** - No Ollama installation needed
✅ **Better quality** - GPT-4o-mini is more capable
✅ **Faster startup** - No model loading time
✅ **Scalable** - No GPU limitations
✅ **Always available** - Cloud-based reliability
✅ **Better embeddings** - State-of-the-art retrieval

---

## 🔧 Troubleshooting

### Error: "Invalid API key"
- Check your API key at https://platform.openai.com/api-keys
- Make sure it's correctly set in `config.py`

### Error: "Rate limit exceeded"
- You've hit OpenAI's rate limit
- Wait a few seconds and try again
- Consider upgrading your OpenAI plan

### Error: "FAISS index not found"
- Run `python ingest.py` to rebuild the index
- Make sure `faiss_medical_index/` folder exists

### Slow responses?
- First request is slower (cold start)
- Subsequent requests are faster
- OpenAI API latency is typically 1-3 seconds

---

## 📚 Documentation

- **Full migration guide**: `OPENAI_MIGRATION_COMPLETE.md`
- **Changes summary**: `OPENAI_CHANGES_SUMMARY.md`
- **API documentation**: http://localhost:8000/docs (after starting server)

---

## 🔄 Switch Back to Ollama?

If you want to use Ollama again:

1. Restore original `config.py` settings
2. Run `python ingest.py` to rebuild index
3. Start Ollama: `ollama serve`
4. Pull models: `ollama pull mistral:7b-instruct`

See `OPENAI_MIGRATION_COMPLETE.md` for details.

---

## ✨ You're All Set!

Your Medical RAG Pipeline is now powered by OpenAI. Enjoy better quality responses with zero local setup! 🎉

**Next**: Start the server and test with your Spring Boot backend!

```bash
python api_server.py
```

Then test from Spring Boot:
```bash
cd ../Backend
java -jar target/anc-service-1.0.0.jar
```

Happy coding! 🚀
