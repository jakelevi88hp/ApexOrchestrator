# Open WebUI Integration Guide

## 🎉 Connect Apex Orchestrator to Open WebUI

This guide will help you set up Open WebUI (ChatGPT-style interface) with your Apex Orchestrator.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Get Your Shared Key

```powershell
# Look in your .env file for APEX_SHARED_KEY
# Or generate a new one:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy this key - you'll need it in Step 4.

### Step 2: Start Open WebUI

```powershell
# Start the Open WebUI container
docker-compose up -d open-webui

# Wait for it to start (about 30 seconds)
Start-Sleep -Seconds 30

# Check if it's running
docker-compose ps
```

### Step 3: Open Open WebUI

Open your browser to: **http://localhost:3000**

### Step 4: Add the Apex Orchestrator Tool

1. **In Open WebUI**, click your profile icon (top right)
2. Click **"Admin Panel"** → **"Functions"**
3. Click **"+" (Create Function)**
4. Click **"Import from file"** or paste the code
5. **Copy the entire contents** of `apex_orchestrator_tool.py` (this directory)
6. Click **"Save"**

### Step 5: Configure the Tool

1. After saving, click the **"Valves" tab**
2. Set these values:
   - **APEX_BASE_URL**: `http://host.docker.internal:8000`
   - **APEX_SHARED_KEY**: *[Your key from Step 1]*
   - **ENABLE_CITATION**: `true`
3. Click **"Save"**

### Step 6: Test It!

Start a new chat and try:

```
List all files in the current directory
```

or

```
Check the status of Apex Orchestrator
```

The AI will automatically use your Apex Orchestrator tool! 🎉

---

## 📚 What You Can Do

### Execute Tasks
```
Create a file called test.txt with content "Hello World"
```

```
Make an HTTP GET request to https://api.github.com
```

```
Run the command: dir
```

### Check System Status
```
What's the status of Apex Orchestrator?
```

```
Show me the system metrics
```

### Complex Operations
```
Create a Python script that prints the current date, save it as date.py, 
and then execute it
```

---

## 🔧 Advanced Configuration

### Enable Authentication

Edit `docker-compose.yml`:

```yaml
open-webui:
  environment:
    - WEBUI_AUTH=true  # Change to true
```

Then restart:
```powershell
docker-compose restart open-webui
```

Now you'll need to create an account on first visit.

### Change Port

Edit `docker-compose.yml`:

```yaml
open-webui:
  ports:
    - "8080:8080"  # Change 3000 to your preferred port
```

### Use OpenAI Models

In your `.env` file:

```bash
ORCH_MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

Then Open WebUI will use GPT-4 for the interface, and Apex Orchestrator for execution.

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│              Open WebUI (Port 3000)             │
│           ChatGPT-style Interface               │
│                                                 │
└─────────────┬───────────────────────────────────┘
              │
              │ (User types natural language)
              │
              ▼
┌─────────────────────────────────────────────────┐
│         LLM (Ollama / OpenAI)                   │
│  - Understands user intent                      │
│  - Decides to use Apex Orchestrator tool        │
└─────────────┬───────────────────────────────────┘
              │
              │ (Calls execute_task function)
              │
              ▼
┌─────────────────────────────────────────────────┐
│        Apex Orchestrator Tool                   │
│  - Authenticates with HMAC                      │
│  - Sends request to /nlm/run                    │
└─────────────┬───────────────────────────────────┘
              │
              │ (POST /nlm/run)
              │
              ▼
┌─────────────────────────────────────────────────┐
│       Apex Orchestrator (Port 8000)             │
│  - Plans the task                               │
│  - Executes tools (shell, file, http, etc.)    │
│  - Returns results                              │
└─────────────────────────────────────────────────┘
```

---

## 🔒 Security

### Authentication Methods

1. **HMAC Signature** (Already implemented)
   - Every request is signed with your shared key
   - Timestamp prevents replay attacks
   - Very secure

2. **Open WebUI Authentication** (Optional)
   - Set `WEBUI_AUTH=true` in docker-compose
   - Users need accounts to access

3. **Network Isolation**
   - Open WebUI and Apex Orchestrator on same Docker network
   - No external exposure required

### Best Practices

✅ **DO:**
- Use strong shared keys (32+ characters)
- Enable Open WebUI authentication in production
- Keep shared key secret
- Monitor logs regularly

❌ **DON'T:**
- Share your shared key publicly
- Use simple passwords
- Expose ports to the internet without firewall

---

## 🐛 Troubleshooting

### Issue: "Failed to connect to Apex Orchestrator"

**Solution:**
```powershell
# Check if Apex Orchestrator is running
docker-compose ps

# Check logs
docker-compose logs apex-orchestrator --tail 50

# Restart if needed
docker-compose restart apex-orchestrator
```

### Issue: "Authentication error"

**Solution:**
1. Verify your shared key matches the one in `.env`
2. Check the tool's Valves settings
3. Ensure no extra spaces in the key

```powershell
# View your current key
Get-Content .env | Select-String "APEX_SHARED_KEY"
```

### Issue: Open WebUI won't start

**Solution:**
```powershell
# Check logs
docker-compose logs open-webui --tail 50

# Pull latest image
docker-compose pull open-webui

# Restart
docker-compose up -d open-webui --force-recreate
```

### Issue: Tool not appearing in chat

**Solution:**
1. Make sure you saved the function
2. Enable the function (toggle switch)
3. Refresh your browser
4. Try a new chat

---

## 📊 Usage Examples

### Example 1: File Operations
```
User: Create a folder called "projects" and inside it create a file 
called "todo.txt" with these items:
- Learn Python
- Build AI app
- Deploy to production

AI: [Uses execute_task tool]
✅ Task Executed Successfully

Intent: Create folder and file with content

Results (2 steps):
Step 1
Created directory: projects

Step 2
Created file: projects/todo.txt
```

### Example 2: System Information
```
User: What's the system status?

AI: [Uses check_status tool]
🤖 Apex Orchestrator Status

Service: ✅
- Version: 1.0.0
- Environment: production
- Timestamp: 2025-10-17T12:00:00Z

Health Checks:
- ✅ Work Dir: healthy
- ✅ Log Dir: healthy
- ✅ Ollama: healthy

🤖 Autonomous Agent:
- Enabled: ❌ No
- Modifications: ✅ Disabled
- Kill Switch: ✅ Inactive
```

### Example 3: API Requests
```
User: Fetch data from https://api.github.com/repos/python/cpython

AI: [Uses execute_task tool]
✅ Task Executed Successfully

Intent: Fetch GitHub repository information

Results (1 steps):
Step 1
{
  "name": "cpython",
  "full_name": "python/cpython",
  "description": "The Python programming language",
  "stargazers_count": 54321,
  ...
}
```

---

## 🎨 Customization

### Add More Functions

You can create additional functions for specific workflows:

**Example: Quick Status Function**

```python
async def quick_status(self) -> str:
    """Get quick Apex Orchestrator status"""
    response = requests.get(f"{self.valves.APEX_BASE_URL}/health")
    data = response.json()
    return "✅ Healthy" if data.get("ok") else "❌ Unhealthy"
```

### Modify the Tool

Edit `apex_orchestrator_tool.py` and update the function in Open WebUI.

---

## 📖 Resources

- **Open WebUI Docs**: https://docs.openwebui.com/
- **Apex Orchestrator API**: http://localhost:8000/docs
- **Tool Functions Guide**: https://docs.openwebui.com/tutorials/functions/

---

## 🆘 Getting Help

### Check Logs
```powershell
# Open WebUI logs
docker-compose logs open-webui -f

# Apex Orchestrator logs
docker-compose logs apex-orchestrator -f

# All logs
docker-compose logs -f
```

### Test API Directly
```powershell
# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/health

# Test Open WebUI
Invoke-WebRequest -Uri http://localhost:3000
```

### Restart Everything
```powershell
docker-compose down
docker-compose up -d
```

---

## 🎉 Success!

You now have a beautiful ChatGPT-style interface connected to your powerful Apex Orchestrator!

**Next Steps:**
1. Try different commands
2. Explore the autonomous agent features
3. Customize the tool for your workflow
4. Share with your team

**Enjoy! 🚀**

