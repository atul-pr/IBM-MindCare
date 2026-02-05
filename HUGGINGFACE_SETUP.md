# HuggingFace API Integration Guide

## 🎯 What's New

Your chatbot now uses **HuggingFace's free Inference API** for fully conversational AI responses!

- ✅ **Model:** microsoft/DialoGPT-medium (conversational AI)
- ✅ **Free tier:** No payment required
- ✅ **Fallback:** Pattern-based responses if API unavailable
- ✅ **Smart:** Tries API first, falls back automatically

---

## 🔑 Get Your Free API Key (2 Minutes)

### Step 1: Create HuggingFace Account
1. Go to: **https://huggingface.co/join**
2. Sign up (free, no credit card needed)
3. Verify your email

### Step 2: Generate API Token
1. Go to: **https://huggingface.co/settings/tokens**
2. Click **"New token"**
3. Name: `mental-health-chatbot`
4. Type: **Read** (default)
5. Click **"Generate token"**
6. **Copy the token** (starts with `hf_...`)

### Step 3: Add to Your Project
1. In your project folder, create a file named `.env`
2. Add this line:
   ```
   HUGGINGFACE_API_KEY=hf_your_token_here
   ```
3. Save the file

---

## 🚀 Setup Instructions

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For API calls
- `python-dotenv` - For loading .env file

### 2. Create .env File
```bash
# Copy the example
copy .env.example .env

# Edit .env and add your API key
notepad .env
```

Add your key:
```
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Restart Server
```bash
# Stop current server (Ctrl+C)
# Then restart
python app.py
```

---

## 🧪 Test the AI

### Without API Key (Pattern-Based)
```
You: I'm feeling anxious
Bot: [Pre-defined empathetic response about anxiety]
```

### With API Key (Full AI)
```
You: I'm feeling anxious
Bot: [Natural, contextual conversation based on your specific message]
```

The AI will:
- Remember conversation context
- Provide personalized responses
- Adapt to your specific situation
- Sound more natural and human-like

---

## 🔄 How It Works

```
User Message → Try HuggingFace API
                    ↓
              [API Available?]
                    ↓
        Yes → Natural AI Response
                    ↓
         No → Pattern-Based Fallback
```

**Benefits:**
- ✅ Works even without API key
- ✅ No errors if API is down
- ✅ Seamless fallback
- ✅ Free forever (HuggingFace free tier)

---

## 📊 API Limits (Free Tier)

- **Requests:** ~1,000 per day
- **Rate limit:** ~30 requests per minute
- **Cost:** $0 (completely free)
- **No credit card:** Required

**More than enough for hackathon demo and testing!**

---

## 🎨 Example Conversation (With API)

```
You: My girlfriend just broke up with me and I don't know what to do

Bot: I'm really sorry you're going through this. Breakups can be incredibly 
     painful, and what you're feeling right now is completely valid. It's 
     normal to feel lost and confused. Can you tell me a bit more about 
     what happened? Sometimes talking about it can help.

You: She said she needs space to figure things out

Bot: That must be really hard to hear, especially when you care about her. 
     The uncertainty of "needing space" can be even more difficult than a 
     clear ending. Right now, the most important thing is taking care of 
     yourself. Have you been able to talk to any friends or family about 
     this?
```

**Much more natural and contextual than pattern-based responses!**

---

## 🛠️ Troubleshooting

### "API key not found"
- Make sure `.env` file exists (not `.env.example`)
- Check the key starts with `hf_`
- Restart the server after adding key

### "API request failed"
- Check internet connection
- Verify API key is valid
- System automatically falls back to pattern responses

### "Module not found: requests"
- Run: `pip install -r requirements.txt`
- Make sure virtual environment is activated

---

## 🎯 For Hackathon Demo

### Option 1: With API Key (Recommended)
- Get free HuggingFace token (2 minutes)
- Add to `.env` file
- Restart server
- **Demo with fully conversational AI** ✨

### Option 2: Without API Key
- Skip API setup
- Use pattern-based responses
- Still works perfectly for demo
- **Mention "can integrate any LLM API"**

---

## 🚀 Next Steps

Want even better responses? You can easily swap to:

1. **OpenAI GPT-3.5** (paid, $0.002 per 1K tokens)
2. **Anthropic Claude** (paid, similar pricing)
3. **Google Gemini** (free tier available)

Just update the API call in `ai.py` - the structure is already there!

---

**Your chatbot is now AI-powered! 🎉**
