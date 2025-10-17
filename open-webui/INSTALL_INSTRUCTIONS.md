# 🚀 Open WebUI Tool - 2-Minute Setup

## ✅ Your System Status
- **Apex Orchestrator:** ✅ Running & Healthy (Port 8000)
- **Open WebUI:** ✅ Running & Healthy (Port 8080)
- **Credentials:** ✅ Pre-configured in READY_TO_COPY.py

---

## 📋 Installation (Just 3 Steps!)

### Step 1: Open Open WebUI
Click here or copy to browser:
```
http://localhost:8080
```

### Step 2: Navigate to Functions
1. Click your **profile icon** (top right)
2. Click **"Admin Panel"**
3. Click **"Functions"** in the sidebar
4. Click the **"+"** button (Create New Function)

### Step 3: Copy & Paste
1. Open the file: **`open-webui/READY_TO_COPY.py`** (in this project)
2. **Select ALL** the code (Ctrl+A)
3. **Copy** it (Ctrl+C)
4. **Paste** into the Open WebUI code editor
5. Click **"Save"** (bottom right)
6. **Enable** the toggle switch at the top

---

## ✅ Test It!

Start a new chat and try:

```
Check the Apex Orchestrator status
```

Or:

```
List all files in the current directory
```

Or:

```
Create a file called test.txt with the text "Hello from Open WebUI!"
```

The AI will automatically use the Apex Orchestrator tool! 🎉

---

## 🎯 What You Get

With this tool installed, you can:

### File Operations
```
Create a new folder called "projects"
Show me the contents of the logs directory
Delete the file test.txt
```

### System Commands
```
What's the current date and time?
Check disk space
Show running Docker containers
```

### API Requests
```
Get the latest data from https://api.github.com
Send a POST request to my webhook
```

### Python Execution
```
Run a Python script that calculates pi to 10 decimals
Execute Python code to generate a random password
```

---

## 🔧 Troubleshooting

### Issue: Tool not appearing in chat
**Solution:** Make sure you enabled the toggle switch after saving

### Issue: Connection errors
**Solution:** Verify Apex is running:
```powershell
docker-compose ps
Invoke-WebRequest http://localhost:8000/health
```

### Issue: Authentication errors
**Solution:** The key is already pre-configured in READY_TO_COPY.py - no changes needed!

---

## 📍 File Location

The ready-to-use file is here:
```
C:\ApexOrchestrator\open-webui\READY_TO_COPY.py
```

---

## 🎨 Alternative: If You Want to Customize

If you want to change the URL or key later:

Edit lines 31-32 in the Open WebUI function editor:
```python
APEX_BASE_URL = "http://host.docker.internal:8000"  # Change if needed
APEX_SHARED_KEY = "XGR8IDzftIqPBLL5t62CU1OUYXfi-fbAnS7BNqa-AyA"  # Your key
```

---

## 🎊 That's It!

Your Open WebUI now has autonomous task execution powered by Apex Orchestrator!

**Enjoy your AI-powered assistant!** 🚀

