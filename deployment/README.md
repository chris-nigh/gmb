# Deployment Guide for GMB Fantasy Football Dashboard

This directory contains configuration files for various deployment methods.

## Quick Start Deployment Options

### 1. Streamlit Community Cloud (Easiest)

**Best for**: Free hosting, automatic updates, no server maintenance

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and select your repository
4. Add secrets in "Advanced settings":
   ```toml
   GMB_LEAGUE_ID = "123456"
   GMB_YEAR = "2025"
   GMB_ESPN_S2 = "your_cookie_value"
   GMB_SWID = "{YOUR-SWID-HERE}"
   ```
5. Deploy!

### 2. Docker (Most Portable)

**Best for**: Self-hosting, consistent environments

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t gmb-dashboard .
docker run -p 8501:8501 \
  -e GMB_LEAGUE_ID="123456" \
  -e GMB_YEAR="2025" \
  -e GMB_ESPN_S2="your_cookie" \
  -e GMB_SWID="your_swid" \
  gmb-dashboard
```

### 3. Linux Server with Systemd

**Best for**: VPS/dedicated servers, custom domains

```bash
# 1. Clone and install
git clone https://github.com/your-username/gmb.git /opt/gmb
cd /opt/gmb
pip install -e .

# 2. Copy and edit service file
sudo cp deployment/gmb-dashboard.service /etc/systemd/system/
sudo nano /etc/systemd/system/gmb-dashboard.service
# Edit the Environment variables with your values

# 3. Start service
sudo systemctl daemon-reload
sudo systemctl enable gmb-dashboard
sudo systemctl start gmb-dashboard
sudo systemctl status gmb-dashboard

# 4. (Optional) Setup Nginx reverse proxy
sudo cp deployment/nginx.conf /etc/nginx/sites-available/gmb-dashboard
sudo ln -s /etc/nginx/sites-available/gmb-dashboard /etc/nginx/sites-enabled/
sudo nano /etc/nginx/sites-available/gmb-dashboard
# Edit server_name with your domain
sudo nginx -t
sudo systemctl reload nginx

# 5. (Optional) Get SSL certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

All deployment methods require these environment variables:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `GMB_LEAGUE_ID` | Yes | `123456` | Your ESPN league ID |
| `GMB_YEAR` | Yes | `2025` | Fantasy season year |
| `GMB_ESPN_S2` | Private leagues | `AEArMPrD3za...` | ESPN session cookie |
| `GMB_SWID` | Private leagues | `{XXXXXXXX-...}` | ESPN user identifier |

## Getting ESPN Credentials

For **private leagues**, you need cookies from ESPN:

1. **Log into ESPN Fantasy Football** in Chrome/Firefox
2. **Open Developer Tools** (F12)
3. Go to **Network** tab
4. **Refresh the page**
5. Find any request to `fantasy.espn.com`
6. In **Request Headers**, copy:
   - `espn_s2`: Long string starting with letters/numbers
   - `SWID`: Format like `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`

**Important**: These cookies expire after ~2 months, so you'll need to update them periodically.

## Updating the Deployment

### Streamlit Cloud
- Push changes to GitHub
- App auto-updates within minutes

### Docker
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

### Systemd
```bash
cd /opt/gmb
git pull
sudo systemctl restart gmb-dashboard
```

## Monitoring

### Check if app is running
```bash
# Streamlit Cloud: Check dashboard at https://share.streamlit.io
# Docker: docker-compose logs -f
# Systemd: sudo systemctl status gmb-dashboard
# Direct: curl http://localhost:8501/_stcore/health
```

### Common Issues

**Problem**: "Configuration Error: GMB_LEAGUE_ID is required"
- **Fix**: Set environment variables correctly

**Problem**: "Error loading league data: 401/403"
- **Fix**: Update ESPN_S2 and SWID cookies (they expired)

**Problem**: "KeyError: 'team_id'"
- **Fix**: Already fixed in latest version, pull updates

**Problem**: App shows old data
- **Fix**: Restart the app (ESPN data is cached)

## Security Notes

- Never commit `.streamlit/secrets.toml` or `.env` files
- Keep ESPN cookies private (they provide access to your account)
- Use HTTPS in production (included in nginx config)
- Restrict access if deploying publicly (add authentication)

## Platform-Specific Instructions

### AWS EC2
1. Launch Ubuntu 22.04 instance
2. Follow "Linux Server with Systemd" instructions
3. Configure security group to allow port 80/443

### Google Cloud Run
```bash
gcloud run deploy gmb-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GMB_LEAGUE_ID=123456,GMB_YEAR=2025
```

### Heroku
```bash
heroku create your-app-name
heroku config:set GMB_LEAGUE_ID=123456
heroku config:set GMB_YEAR=2025
git push heroku main
```

### Railway
1. Connect GitHub repository
2. Add environment variables in dashboard
3. Deploy automatically

## Support

For issues, check:
- [Streamlit Docs](https://docs.streamlit.io/deploy)
- [Project Issues](https://github.com/your-username/gmb/issues)
