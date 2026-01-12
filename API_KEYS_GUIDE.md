# API Keys Setup Guide

## 🔑 Required API Keys

### 1. OpenAI API Key

**What it's used for:**
- GPT-4 language model for generating responses
- Text embeddings for document search

**How to get it:**
1. Go to https://platform.openai.com/signup
2. Sign up for an account
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Pricing:**
- **NOT FREE** - Pay-as-you-go pricing
- New accounts get $5 free credits (expires after 3 months)
- GPT-4o-Mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- Embeddings: ~$0.02 per 1M tokens
- Estimate: ~$0.10-0.50 for testing with a few documents and queries

**Free Credit:** 
- New signups get $5 free credit valid for 3 months
- Enough for thorough testing and demo

**Monitoring:**
- Check usage at https://platform.openai.com/usage
- Set spending limits at https://platform.openai.com/account/billing/limits

---

### 2. SerpAPI Key (for Web Search)

**What it's used for:**
- Real-time web search in LLM responses
- Optional feature - can skip if not using web search

**How to get it:**
1. Go to https://serpapi.com/users/sign_up
2. Sign up for an account
3. Go to https://serpapi.com/manage-api-key
4. Copy your API key

**Pricing:**
- **FREE TIER:** 100 searches/month
- Paid plans start at $50/month for 5,000 searches
- Free tier is sufficient for testing and demo

**Alternative:** Leave empty if you don't need web search feature

---

## 🆓 Free Alternatives

### Option 1: Use Free Tiers (Recommended)

**Setup:**
```env
# .env file
OPENAI_API_KEY=sk-your-key-here  # $5 free credit for new accounts
SERPAPI_API_KEY=your-key-here     # 100 free searches/month
```

This gives you enough to:
- Test the full application
- Upload 5-10 sample PDFs
- Run 50-100 queries
- Demo all features

---

### Option 2: OpenAI Alternatives (Requires Code Changes)

If you want completely free options:

**A. Ollama (Local LLM)**
- Runs models locally (no API key needed)
- Free and private
- Requires modifying `backend/app/components/llm_engine.py`
- Models: Llama 2, Mistral, etc.
- Link: https://ollama.ai

**B. Hugging Face API (Free Tier)**
- Some models have free inference API
- Requires code changes
- Link: https://huggingface.co/inference-api

**C. Google Gemini API (Has Free Tier)**
- Better free tier than OpenAI
- 60 requests/minute free
- Requires modifying LLM component
- Link: https://makersuite.google.com/app/apikey

---

### Option 3: Skip Web Search

You can disable web search and still use the core features:

```env
# .env file
OPENAI_API_KEY=sk-your-key-here
SERPAPI_API_KEY=  # Leave empty - web search will be skipped
```

The application will work without web search, you'll just need to disable the web search toggle in the LLM component UI.

---

## 💡 Recommended Approach for Testing

**For this assignment/demo:**

1. **OpenAI**: Use the $5 free credit
   - Sign up at https://platform.openai.com
   - Get your free $5 credit
   - Use GPT-4o-Mini (cheapest model)
   - This is enough for full demo

2. **SerpAPI**: Use free tier
   - Sign up at https://serpapi.com
   - Get 100 free searches/month
   - Only enable web search when needed

**Total Cost:** $0 (using free tiers)

---

## 🔧 Setup Instructions

1. **Get OpenAI Key:**
   ```bash
   # Visit: https://platform.openai.com/api-keys
   # Create new key, copy it
   ```

2. **Get SerpAPI Key (Optional):**
   ```bash
   # Visit: https://serpapi.com/manage-api-key
   # Copy your free tier key
   ```

3. **Configure .env:**
   ```bash
   cd PlanetAiAssignment
   cp .env.example .env
   nano .env  # or use any text editor
   ```

4. **Add your keys:**
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   SERPAPI_API_KEY=your_serpapi_key_or_leave_empty
   ```

5. **Also update backend/.env:**
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env
   # Add the same keys
   ```

---

## 📊 Cost Estimation

**Typical usage for testing:**
- Upload 5 PDFs (50 pages each): ~$0.10 in embeddings
- 50 chat queries: ~$0.20 in GPT-4o-Mini costs
- 20 web searches: Free (within SerpAPI free tier)

**Total: ~$0.30** - Well within the $5 free credit

---

## ⚠️ Important Notes

- **Never commit .env files to GitHub** (already in .gitignore)
- **OpenAI credits expire** after 3 months for new accounts
- **Monitor your usage** to avoid unexpected charges
- **Use GPT-4o-Mini** not GPT-4 (100x cheaper)
- **SerpAPI free tier** resets monthly

---

## 🆘 If You Don't Want to Use Paid APIs

You can modify the code to use:
- **Ollama** for local LLM (completely free)
- **Sentence Transformers** for embeddings (free)
- **DuckDuckGo** for web search (free, no API key)

This requires code modifications but makes it 100% free. Let me know if you need help with this!

---

## 📞 Support

If you have issues getting API keys:
- OpenAI: https://help.openai.com
- SerpAPI: https://serpapi.com/contact

For free alternatives or code modifications, refer to the implementation plan or ask for guidance.
