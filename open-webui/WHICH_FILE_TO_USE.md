# 📋 Which File Should You Use?

## 🎯 Quick Answer

### If you're adding to **"Functions"** section:
✅ **USE THIS:** `READY_TO_COPY_FUNCTION.py`
- Has `class Function:` (singular)
- Goes in: Admin Panel → **Functions** → "+"

### If you're adding to **"Tools"** section:
✅ **USE THIS:** `READY_TO_COPY.py`
- Has `class Tools:` (plural)
- Goes in: Admin Panel → **Tools** → "+"

---

## 🔍 How To Tell Which Section You're In

### Functions Section (Most Common)
```
Profile Icon → Admin Panel → Functions → "+" button
```
**Use:** `READY_TO_COPY_FUNCTION.py`

### Tools Section
```
Profile Icon → Admin Panel → Tools → "+" button
```
**Use:** `READY_TO_COPY.py`

---

## ✅ Installation Steps

### Step 1: Pick the Right File
- In **Functions**? Use `READY_TO_COPY_FUNCTION.py`
- In **Tools**? Use `READY_TO_COPY.py`

### Step 2: Copy & Paste
1. Open the file in your editor
2. Select ALL (Ctrl+A)
3. Copy (Ctrl+C)
4. Paste into Open WebUI code editor
5. Click **Save**

### Step 3: Enable
- Toggle the switch to **ON**
- Look for the green checkmark

### Step 4: Test
In a new chat, type:
```
Check the Apex Orchestrator status
```

---

## 🐛 Error Messages & Solutions

### Error: "No function class in module"
❌ **Problem:** You used `READY_TO_COPY.py` (Tools class) in the Functions section  
✅ **Solution:** Use `READY_TO_COPY_FUNCTION.py` instead

### Error: "No tools class in module"
❌ **Problem:** You used `READY_TO_COPY_FUNCTION.py` (Function class) in the Tools section  
✅ **Solution:** Use `READY_TO_COPY.py` instead

### Error: "Connection error"
❌ **Problem:** Apex Orchestrator not running  
✅ **Solution:** Run `docker-compose up -d`

### Error: "Bad signature"
❌ **Problem:** Wrong shared key  
✅ **Solution:** Update line 33 with your actual key from `.env`

---

## 📁 File Reference

| File Name | Class | Where to Use |
|-----------|-------|--------------|
| `READY_TO_COPY_FUNCTION.py` | `class Function:` | **Functions** section ← **USE THIS** |
| `READY_TO_COPY.py` | `class Tools:` | **Tools** section |
| `apex_tool_final.py` | `class Tools:` | Tools section (alternative) |
| `apex_orchestrator_tool.py` | `class Tools:` | Tools (with Valves config) |

---

## 🎯 Recommended Setup

**99% of users should use:**
1. Go to: **Functions** (not Tools)
2. Use file: **`READY_TO_COPY_FUNCTION.py`**
3. This is the simplest and most reliable option

---

## 💡 Pro Tip

Not sure which section you're in? Look at the page title:
- Says **"Functions"** at the top? Use `READY_TO_COPY_FUNCTION.py`
- Says **"Tools"** at the top? Use `READY_TO_COPY.py`

---

## ✅ Both Files Are Identical Except:

The ONLY difference:
```python
# In READY_TO_COPY_FUNCTION.py
class Function:  ← Singular

# In READY_TO_COPY.py
class Tools:  ← Plural
```

Everything else (authentication, logic, credentials) is identical!

---

## 🚀 After Installation

Test with these commands:
```
Check the system status
```
```
What is 5 + 7?
```
```
List files in the current directory
```

The AI will automatically use the Apex Orchestrator tool! 🎉

---

**Need help? Check which section you're in and use the matching file!**

