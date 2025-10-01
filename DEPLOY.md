# 🚀 Quick Deployment Guide

Choose your deployment method and follow the steps:

---

## 🌟 Option 1: Streamlit Cloud (Recommended)
**Time: 5 minutes | Cost: Free | Difficulty: Easy**

1. **Run setup script:**
   ```bash
   ./deployment/setup-deploy.sh
   ```
   Choose option 1 and follow prompts.

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push
   ```

3. **Deploy on Streamlit:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository → `app.py`
   - Copy secrets from script output
   - Deploy!

4. **Done!** App will be at `https://your-app.streamlit.app`

---

## 🐳 Option 2: Docker
**Time: 10 minutes | Cost: Server costs | Difficulty: Medium**

1. **Setup:**
   ```bash
   ./deployment/setup-deploy.sh
   ```
   Choose option 2.

2. **Deploy:**
   ```bash
   docker-compose up -d
   ```

3. **Access:** http://localhost:8501

4. **Monitor:**
   ```bash
   docker-compose logs -f
   ```

---

## 🖥️ Option 3: Linux Server
**Time: 20 minutes | Cost: Server costs | Difficulty: Advanced**

1. **Setup:**
   ```bash
   ./deployment/setup-deploy.sh
   ```
   Choose option 3.

2. **Install service:**
   ```bash
   sudo cp /tmp/gmb-dashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable gmb-dashboard
   sudo systemctl start gmb-dashboard
   ```

3. **Check status:**
   ```bash
   sudo systemctl status gmb-dashboard
   ```

4. **(Optional) Add HTTPS:**
   ```bash
   sudo cp deployment/nginx.conf /etc/nginx/sites-available/gmb
   sudo ln -s /etc/nginx/sites-available/gmb /etc/nginx/sites-enabled/
   # Edit the file with your domain
   sudo nano /etc/nginx/sites-available/gmb
   sudo certbot --nginx
   ```

---

## 🔑 Getting ESPN Credentials

For **private leagues** only:

1. Open ESPN Fantasy in Chrome/Firefox
2. Press `F12` → Network tab
3. Refresh page
4. Click any `fantasy.espn.com` request
5. Find in Headers:
   - `Cookie: espn_s2=...` (copy value)
   - `Cookie: SWID=...` (copy value)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Configuration Error" | Set environment variables |
| "401/403 error" | Update ESPN cookies (expired) |
| App won't start | Check `docker-compose logs -f` or `systemctl status` |
| Can't access app | Check firewall, open port 8501 |

---

## 📚 More Info

- **Detailed guide:** `deployment/README.md`
- **Checklist:** `deployment/CHECKLIST.md`
- **Main README:** `README.md`

---

## 🎯 What's Next?

After deployment:

1. ✅ Test all 4 tabs work
2. ✅ Share URL with league
3. ✅ Set calendar reminder to refresh cookies (every 2 months)
4. ✅ Star the repo ⭐

**Need help?** Open an issue on GitHub!
