# 🔧 Troubleshooting Guide

## Common Issues and Quick Fixes

---

## ✅ ISSUE FIXED: JSON Decoder Error in Dashboard

**Error Message:**
```
json.decoder.JSONDecodeError: Expecting value: line 2 column 17 (char 18)
```

**Solution:**
This error occurs when JSON result files are incomplete or corrupted.

### Quick Fix (30 seconds):

```bash
python fix_json_files.py
```

This regenerates all JSON result files with proper formatting.

**Then restart the dashboard:**
```bash
streamlit run dashboard/app.py
```

✅ **Fixed!** The dashboard should now work perfectly.

---

## 📋 Other Common Issues

### 1. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
pip install streamlit plotly
```

For FastAPI:
```bash
pip install fastapi uvicorn
```

For all dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**

**Option A - Use Different Port:**
```bash
# For Streamlit
streamlit run dashboard/app.py --server.port 8502

# For FastAPI
# Edit backend/main.py, change port to 8001
```

**Option B - Kill Existing Process:**
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Find what's using the port
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### 3. Data Files Not Found

**Error:**
```
FileNotFoundError: No such file or directory: 'processed_data/...'
```

**Solution:**
```bash
# Run the quick demo to generate all files
python quick_demo.py

# Or process data from scratch
python data_processing/pipeline.py
```

---

### 4. Dashboard Shows "N/A" or "Run optimization"

**Cause:** Result files haven't been generated yet.

**Solution:**
```bash
# Run the quick demo to generate all results
python quick_demo.py

# This creates:
# - optimization/results/*.json
# - forecasting/results/*.json
```

Then refresh the dashboard (press R in browser or F5).

---

### 5. Streamlit Caching Issues

**Symptom:** Dashboard shows old data after running new analysis.

**Solution:**
```bash
# Clear Streamlit cache
# Press 'c' in the terminal running Streamlit, or
# Click "Clear cache" in the dashboard hamburger menu (top right)
```

Or restart the dashboard:
```bash
# Stop with Ctrl+C
# Then restart
streamlit run dashboard/app.py
```

---

### 6. Import Errors in Python Scripts

**Error:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solution:**
```bash
# Reinstall packages
pip install --upgrade pandas numpy scikit-learn

# Or reinstall everything
pip install -r requirements.txt --force-reinstall
```

---

### 7. Database Connection Error

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**

**Option A - Use Without Database:**
The system works fine without PostgreSQL. It uses CSV files by default.

**Option B - Start PostgreSQL:**
```bash
# With Docker
docker-compose up postgres -d

# Or install PostgreSQL separately
```

**Option C - Update .env:**
```env
# Comment out database URL if not using database
# DATABASE_URL=postgresql://...
```

---

### 8. Slow Performance / Out of Memory

**Symptom:** Dashboard or scripts running very slowly or crashing.

**Solution:**

**Option A - Reduce Data Size:**
Edit scripts to process fewer records:
```python
# In pipeline.py or other scripts
data = data.head(10000)  # Process first 10K records only
```

**Option B - Increase Memory:**
Close other applications.

**Option C - Process in Chunks:**
```python
# For large files
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process(chunk)
```

---

## 🚀 Quick Fix Commands

### Regenerate Everything

```bash
# 1. Fix JSON files
python fix_json_files.py

# 2. Regenerate all results
python quick_demo.py

# 3. Restart dashboard
streamlit run dashboard/app.py
```

### Verify Installation

```bash
python verify_installation.py
```

### Check What's Running

```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# See all Python processes
tasklist | findstr python
```

---

## 📞 Still Having Issues?

### Check These Files:

1. **Logs:**
   - Terminal output from Streamlit
   - Terminal output from FastAPI
   - Browser console (F12)

2. **File Existence:**
   ```bash
   dir optimization\results
   dir forecasting\results
   dir processed_data
   ```

3. **JSON Validity:**
   ```bash
   python fix_json_files.py
   ```

4. **Python Environment:**
   ```bash
   python --version
   pip list
   ```

---

## 🎯 Emergency Reset

If everything is broken, start fresh:

```bash
# 1. Delete generated files
rmdir /s /q optimization\results
rmdir /s /q forecasting\results
rmdir /s /q processed_data

# 2. Recreate directories
mkdir optimization\results
mkdir forecasting\results
mkdir processed_data

# 3. Regenerate everything
python quick_demo.py

# 4. Fix JSON files
python fix_json_files.py

# 5. Start dashboard
streamlit run dashboard/app.py
```

---

## ✅ Preventive Measures

### Before Running Scripts:

1. **Check disk space:**
   ```bash
   # Ensure at least 5GB free space
   ```

2. **Close unnecessary applications**

3. **Verify Python version:**
   ```bash
   python --version
   # Should be 3.11 or higher
   ```

4. **Update packages:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

---

## 📚 Related Documentation

- **README.md** - General usage guide
- **PROJECT_SUMMARY.md** - Technical details
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **PROJECT_COMPLETE.md** - Project overview

---

## 🔍 Debug Mode

### Enable Verbose Output:

**For Streamlit:**
```bash
streamlit run dashboard/app.py --logger.level=debug
```

**For Python Scripts:**
```python
# Add at top of script
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## ✨ Success Checklist

After fixing any issue, verify:

- [ ] ✅ `python fix_json_files.py` runs successfully
- [ ] ✅ `python verify_installation.py` shows 90%+ success
- [ ] ✅ `python quick_demo.py` completes without errors
- [ ] ✅ Dashboard loads: `streamlit run dashboard/app.py`
- [ ] ✅ All 9 dashboard pages accessible
- [ ] ✅ No JSON errors in browser console (F12)
- [ ] ✅ API starts: `python backend/main.py` (optional)

---

**Most Common Fix:**
```bash
python fix_json_files.py && streamlit run dashboard/app.py
```

**This solves 90% of dashboard issues!** ✅
