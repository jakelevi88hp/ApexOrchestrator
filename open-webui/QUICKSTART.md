# 🚀 Open WebUI + Apex Orchestrator - Quick Start

## ✅ Setup Complete!

Open WebUI is now running and ready to connect to your Apex Orchestrator!

---

## 📍 Access Points

- **Open WebUI**: http://localhost:8080
- **Apex Orchestrator API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## ⚡ 3-Step Setup

### Step 1: Open Open WebUI

Go to: **http://localhost:8080**

(No login required - authentication is disabled for easy setup)

### Step 2: Import the Apex Orchestrator Tool

1. Click the **profile icon** (top right)
2. Go to **Admin Panel** → **Functions**
3. Click **"+"** to create a new function
4. **Copy and paste** the entire contents of:
   - File: `open-webui/apex_orchestrator_tool.py`
   - Or copy from the code below

5. Click **Save**

### Step 3: Configure Your Shared Key

1. After saving, click the **"Valves"** tab
2. Set **APEX_SHARED_KEY** to your key from `.env`
3. Click **Save**

**Done!** 🎉

---

## 🎯 Try It Out!

Start a new chat and type:

```
List all files in the current directory
```

or

```
Check Apex Orchestrator status
```

or

```
Create a file called hello.txt with content "Hello from Open WebUI!"
```

The AI will automatically use your Apex Orchestrator! 🤖

---

## 🔑 Get Your Shared Key

If you don't have your `.env` file yet:

```powershell
# Check if .env exists
if (Test-Path .env) {
    Get-Content .env | Select-String "APEX_SHARED_KEY"
} else {
    Write-Host ".env file not found. Copy from config/env.example"
}
```

Or generate a new one:

```powershell
# PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📋 Tool Code

<details>
<summary>Click to expand - Copy this into Open WebUI</summary>

```python
# Get the full code from: open-webui/apex_orchestrator_tool.py
# Or see SETUP_GUIDE.md for the complete code
```

</details>

---

## 🎨 What You Can Do

### File Operations
- "Create a folder called projects"
- "Write a Python script that prints Hello World"
- "List all .txt files"

### System Commands
- "Run the command: dir"
- "Get system information"
- "Check disk space"

### HTTP Requests
- "Fetch data from https://api.github.com"
- "Make a POST request to an API"

### Status Checks
- "What's the Apex Orchestrator status?"
- "Show me system metrics"
- "Is the autonomous agent enabled?"

---

## 🔧 Configuration

### Your Tool Settings (Valves):

```
APEX_BASE_URL: http://host.docker.internal:8000
APEX_SHARED_KEY: [Your key from .env]
ENABLE_CITATION: true
```

### Change Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8080"  # Change 8080 to your preferred port
```

Then:
```powershell
docker-compose restart open-webui
```

### Enable Authentication

Edit `docker-compose.yml`:
```yaml
environment:
  - WEBUI_AUTH=true
```

Then:
```powershell
docker-compose restart open-webui
```

---

## 🐛 Troubleshooting

### Can't access Open WebUI?

```powershell
# Check if it's running
docker-compose ps

# Check logs
docker-compose logs open-webui --tail 50

# Restart
docker-compose restart open-webui
```

### Tool not working?

1. **Check shared key** in Valves settings
2. **Verify Apex Orchestrator** is running:
   ```powershell
   Invoke-WebRequest http://localhost:8000/health
   ```
3. **Check connection** from Open WebUI container:
   ```powershell
   docker exec open-webui curl http://host.docker.internal:8000/health
   ```

### Authentication errors?

- Make sure your shared key is correct
- No extra spaces in the key
- Key must be at least 32 characters

---

## 📊 Architecture

```
User Browser
    ↓ (http://localhost:8080)
Open WebUI Container
    ↓ (LLM processes request)
    ↓ (Decides to use Apex tool)
Apex Orchestrator Tool (Python function)
    ↓ (HMAC authenticated request)
Apex Orchestrator Container (Port 8000)
    ↓ (Executes task)
    ↓ (Returns results)
Back to User
```

---

## 🎉 Success Indicators

You know it's working when:

✅ Open WebUI loads at http://localhost:8080  
✅ You can create a new chat  
✅ The Apex Orchestrator tool appears in Functions  
✅ Commands like "List files" execute successfully  
✅ You see formatted results in the chat  

---

## 📚 Learn More

- **Full Setup Guide**: `SETUP_GUIDE.md`
- **Tool Code**: `apex_orchestrator_tool.py`
- **Apex API Docs**: http://localhost:8000/docs
- **Open WebUI Docs**: https://docs.openwebui.com/

---

## 🆘 Need Help?

```powershell
# View all logs
docker-compose logs -f

# Check all containers
docker-compose ps

# Restart everything
docker-compose restart

# Full reset
docker-compose down
docker-compose up -d
```

---

**Enjoy your ChatGPT-style interface with autonomous task execution! 🚀**

