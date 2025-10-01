# Deployment Checklist for GMB Dashboard

Use this checklist to ensure smooth deployment.

## Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Code is lint-clean (`mypy`, `black`)
- [ ] Configuration tested locally (`streamlit run app.py`)
- [ ] ESPN credentials obtained (for private leagues)
- [ ] `.gitignore` updated (no secrets committed)
- [ ] Documentation updated (`README.md`)

## Streamlit Community Cloud

- [ ] Code pushed to GitHub
- [ ] Account created at [share.streamlit.io](https://share.streamlit.io)
- [ ] Repository connected
- [ ] App created with `app.py` as main file
- [ ] Secrets added:
  - [ ] `GMB_LEAGUE_ID`
  - [ ] `GMB_YEAR`
  - [ ] `GMB_ESPN_S2` (private leagues)
  - [ ] `GMB_SWID` (private leagues)
- [ ] App deployed successfully
- [ ] URL tested and working
- [ ] Shared with league members

## Docker Deployment

- [ ] Docker installed
- [ ] `.env` file created with credentials
- [ ] Image built successfully (`docker build`)
- [ ] Container runs locally (`docker run`)
- [ ] Port 8501 accessible
- [ ] Health check passing
- [ ] docker-compose.yml tested
- [ ] Production environment configured
- [ ] Auto-restart enabled

## Server Deployment (VPS/Cloud)

- [ ] Server provisioned (Ubuntu 22.04 recommended)
- [ ] Python 3.13+ installed
- [ ] Project cloned to `/opt/gmb`
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Systemd service file configured
- [ ] Environment variables set
- [ ] Service enabled and started
- [ ] Service status verified
- [ ] Logs checked for errors
- [ ] Port 8501 accessible (or proxied)

## Nginx Reverse Proxy (Optional)

- [ ] Nginx installed
- [ ] Configuration file created
- [ ] Domain/subdomain configured
- [ ] DNS records updated
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] HTTPS enabled
- [ ] WebSocket support verified
- [ ] Configuration tested (`nginx -t`)
- [ ] Nginx reloaded

## Post-Deployment

- [ ] App loads without errors
- [ ] All tabs functional:
  - [ ] Overview tab
  - [ ] Analytics tab
  - [ ] Power Rankings tab
  - [ ] OIWP Analysis tab
- [ ] Data displays correctly
- [ ] Charts render properly
- [ ] League data refreshes
- [ ] Mobile responsiveness checked
- [ ] Performance acceptable
- [ ] Error handling works
- [ ] Monitoring/logging configured

## Security

- [ ] Secrets not in git repository
- [ ] `.streamlit/secrets.toml` gitignored
- [ ] HTTPS enabled (production)
- [ ] Credentials rotated if needed
- [ ] Access logs reviewed
- [ ] Rate limiting considered (if public)
- [ ] Firewall configured (server deployments)

## Maintenance

- [ ] Update schedule planned
- [ ] Backup strategy defined
- [ ] ESPN cookie refresh process documented
- [ ] Monitoring alerts configured
- [ ] League members notified of URL
- [ ] Usage instructions shared

## Troubleshooting Commands

```bash
# Check if app is running
curl http://localhost:8501/_stcore/health

# View systemd logs
sudo journalctl -u gmb-dashboard -f

# View Docker logs
docker-compose logs -f

# Restart services
sudo systemctl restart gmb-dashboard  # systemd
docker-compose restart                 # Docker

# Check environment variables
env | grep GMB
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "Configuration Error" | Check environment variables are set |
| 401/403 from ESPN | Update expired ESPN cookies |
| Port already in use | Change port or stop conflicting service |
| Module not found | Run `pip install -e .` |
| Charts not rendering | Check plotly is installed |
| Slow performance | Increase server resources |

## Next Steps After Deployment

1. Monitor for 24 hours
2. Check data refreshes correctly
3. Gather user feedback
4. Plan for ESPN cookie refresh
5. Consider adding authentication
6. Set up analytics/monitoring
