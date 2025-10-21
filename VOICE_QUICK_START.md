# 🎤 Voice Interface - Quick Start

## ⚡ 2-Minute Setup

### 1. Install Voice Libraries

```bash
pip install pyttsx3 SpeechRecognition PyAudio gTTS
```

### 2. Start AGI

```bash
python scripts/start.py
```

### 3. Make It Speak!

```python
import requests

requests.post("http://localhost:8000/agi/voice/speak", json={
    "text": "Hello! I can talk now!",
    "emotion": "joy"
})
```

## 🎯 Common Operations

### Make AGI Speak

```bash
curl -X POST http://localhost:8000/agi/voice/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "emotion": "joy"}'
```

### Listen for Voice Input

```bash
curl -X POST http://localhost:8000/agi/voice/listen \
  -H "Content-Type: application/json" \
  -d '{"timeout": 5}'
```

### Complete Voice Interaction

```bash
curl -X POST http://localhost:8000/agi/voice/process \
  -H "Content-Type: application/json" \
  -d '{"timeout": 10}'
```

### Start Voice Conversation

```bash
curl -X POST http://localhost:8000/agi/voice/conversation \
  -H "Content-Type: application/json" \
  -d '{"max_turns": 5}'
```

## 🐍 Python Quick Reference

```python
import requests

BASE = "http://localhost:8000/agi/voice"

# Speak
requests.post(f"{BASE}/speak", json={
    "text": "Hello!",
    "emotion": "joy"
})

# Listen
result = requests.post(f"{BASE}/listen", json={"timeout": 5})
print(f"Heard: {result.json()['text']}")

# Chat (listen + process + speak)
result = requests.post(f"{BASE}/process")
print(f"Heard: {result.json()['heard']}")
print(f"Responded: {result.json()['agi_response']['response']}")

# Conversation
requests.post(f"{BASE}/conversation", json={"max_turns": 5})
```

## 😊 Emotions

Use emotions to modulate voice:

```python
emotions = ["joy", "sadness", "excitement", "anger", "fear", "neutral", "curiosity"]

for emotion in emotions:
    requests.post("http://localhost:8000/agi/voice/speak", json={
        "text": f"I'm feeling {emotion}",
        "emotion": emotion
    })
```

## 🔧 Voice Parameters

```python
# Adjust speed
requests.post("http://localhost:8000/agi/voice/parameters", json={
    "rate": 175  # words per minute (50-300)
})

# Adjust volume
requests.post("http://localhost:8000/agi/voice/parameters", json={
    "volume": 0.8  # 0.0 to 1.0
})
```

## 📊 Status

```bash
# Check voice capabilities
curl http://localhost:8000/agi/voice/status

# Get available voices
curl http://localhost:8000/agi/voice/voices

# View conversation history
curl http://localhost:8000/agi/voice/history
```

## 🎬 Example: Voice Assistant

```python
import requests

def voice_assistant():
    """Simple voice assistant loop"""
    print("Voice Assistant Started")
    print("Say 'goodbye' to exit\n")
    
    while True:
        # Listen
        print("🎤 Listening...")
        result = requests.post("http://localhost:8000/agi/voice/listen", json={
            "timeout": 10
        }).json()
        
        if result['status'] != 'success':
            continue
        
        text = result['text']
        print(f"You: {text}")
        
        # Check for exit
        if 'goodbye' in text.lower():
            requests.post("http://localhost:8000/agi/voice/speak", json={
                "text": "Goodbye!",
                "emotion": "joy"
            })
            break
        
        # Process and respond
        response = requests.post("http://localhost:8000/agi/voice/process").json()
        print(f"AGI: {response['agi_response']['response']}\n")

# Run it
voice_assistant()
```

## 📱 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agi/voice/speak` | POST | Make AGI speak |
| `/agi/voice/listen` | POST | Listen for input |
| `/agi/voice/process` | POST | Complete cycle |
| `/agi/voice/conversation` | POST | Multi-turn chat |
| `/agi/voice/status` | GET | Get status |
| `/agi/voice/parameters` | POST | Adjust voice |
| `/agi/voice/voices` | GET | List voices |
| `/agi/voice/history` | GET | Get history |

## 🆘 Troubleshooting

### No Sound?

```python
# Check status
status = requests.get("http://localhost:8000/agi/voice/status").json()
print(f"Voice enabled: {status['voice_enabled']}")
```

### Can't Hear You?

```python
# Test microphone
result = requests.post("http://localhost:8000/agi/voice/listen", json={
    "timeout": 3
}).json()
print(result)
```

### Check Logs

```bash
tail -f logs/apex_orchestrator.log | grep voice
```

## 📚 Full Documentation

- **Complete Guide**: `docs/VOICE_INTERFACE.md`
- **Test Script**: `python test_voice.py`
- **Integration Guide**: `VOICE_INTEGRATION_COMPLETE.md`

## ✨ Tips

1. **Speak clearly** at moderate pace
2. **Use emotions** for natural responses
3. **Adjust rate** if too fast/slow
4. **Save audio** for later playback
5. **Check history** to review conversations

---

**Your AGI has a voice - start talking!** 🎤🤖

