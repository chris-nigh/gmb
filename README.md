# GMB Fantasy Football Dashboard

A dashboard for tracking ESPN fantasy football leagues with advanced statistics and visualizations.

## Features

- **Live League Data**: Real-time standings, statistics, and team information
- **Interactive Dashboard**: Tabbed interface with multiple views
  - **Overview**: Current standings and league summary
  - **Analytics**: Weekly scoring trends and points analysis
  - **Power Rankings**: Weighted team performance metrics
  - **OIWP Analysis**: Opponent-Independent Winning Percentage with luck factor
  - **Taylor Eras**: Historical win percentage analysis by Taylor Swift album eras
- **Command-Line Tools**:
  - `gmb setup`: Interactive configuration
  - `gmb summary`: Display league standings
  - `gmb oiwp`: Show OIWP analysis in terminal
- **Secure Credential Storage**: Keyring-based storage for ESPN cookies
- **Data Validation**: Built-in checks for data quality and calculation accuracy

## Installation

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

Install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/cnigh/gmb.git
cd gmb
```

2. Run setup (creates venv and installs dependencies):
```bash
make setup
```

Or manually:
```bash
uv venv
uv pip install -e ".[dev]"
```

## Configuration

Run the interactive configuration tool:
```bash
gmb-config --setup
```

This will guide you through setting up:
- ESPN League ID
- Season year
- ESPN credentials (for private leagues)

Configuration is stored in:
- `~/.gmb/config.yaml` for league settings
- System keyring for secure credentials

You can also configure through environment variables:
```bash
export GMB_LEAGUE_ID="your_league_id"
export GMB_YEAR="2024"
export GMB_ESPN_S2="your_espn_s2"  # For private leagues
export GMB_SWID="your_swid"        # For private leagues
```

## Usage

### Web Dashboard

Launch the interactive Streamlit dashboard:
```bash
uv run streamlit run app.py
```

The dashboard includes five main tabs:

1. **📊 Overview**: League standings and summary metrics
2. **📈 Analytics**: Weekly scoring trends and points comparisons
3. **🏆 Power Rankings**: Weighted team performance rankings (60% wins, 40% points)
4. **🎯 OIWP Analysis**:
   - Opponent-Independent Winning Percentage
   - Shows how teams would perform against all opponents
   - Identifies "lucky" teams (winning despite lower scores)
   - Identifies "unlucky" teams (losing despite higher scores)
5. **🎵 Taylor Eras**: Historical performance by Taylor Swift album release eras
   - Win percentage heatmap across different eras
   - Game-by-game era assignment based on actual dates
   - Identifies most dominant owner-era combinations

### Command-Line Interface

View league standings:
```bash
gmb summary
```

Display OIWP analysis:
```bash
gmb oiwp
```

Reconfigure settings:
```bash
gmb setup
```

## Understanding OIWP

**OIWP (Opponent-Independent Winning Percentage)** measures team strength independent of schedule luck:

- **Win %**: Your actual record from head-to-head matchups
- **OIWP**: Win rate if you played against *every* team each week
- **Luck Factor**: Win % minus OIWP
  - **Positive luck**: Winning more than your scores suggest (favorable matchups)
  - **Negative luck**: Losing more than your scores suggest (tough opponents)

Example:
- Team with 75% Win % but 60% OIWP has +15% luck (benefiting from weak opponents)
- Team with 50% Win % but 65% OIWP has -15% luck (facing stronger opponents)

The luck factor should average to zero across all teams (zero-sum property).

## Deployment

### Option 1: Streamlit Community Cloud (Recommended)

The easiest way to deploy your dashboard for free:

1. **Push your code to GitHub** (if not already done)

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"** and connect your GitHub repository

4. **Configure your app**:
   - Repository: `your-username/gmb`
   - Branch: `main` or `master`
   - Main file path: `app.py`

5. **Add secrets** (click "Advanced settings" → "Secrets"):
   ```toml
   GMB_LEAGUE_ID = "your_league_id"
   GMB_YEAR = "2025"
   GMB_ESPN_S2 = "your_espn_s2_cookie"
   GMB_SWID = "your_swid_cookie"
   ```

6. **Deploy** - Your app will be live at `https://your-app-name.streamlit.app`

### Option 2: Docker Deployment

Deploy anywhere using Docker:

1. **Build the image**:
   ```bash
   docker build -t gmb-dashboard .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 \
     -e GMB_LEAGUE_ID="your_league_id" \
     -e GMB_YEAR="2025" \
     -e GMB_ESPN_S2="your_espn_s2" \
     -e GMB_SWID="your_swid" \
     gmb-dashboard
   ```

3. **Access at** `http://localhost:8501`

### Option 3: Traditional Server (VPS/Cloud)

Deploy on any Linux server:

1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3.13
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv
   uv pip install -e .
   ```

2. **Set environment variables**:
   ```bash
   export GMB_LEAGUE_ID="your_league_id"
   export GMB_YEAR="2025"
   export GMB_ESPN_S2="your_espn_s2"
   export GMB_SWID="your_swid"
   ```

3. **Run with systemd** (see `deployment/gmb-dashboard.service`)

4. **Set up reverse proxy** (Nginx/Caddy) for HTTPS

### Getting ESPN Credentials

For **private leagues**, you need ESPN cookies:

1. Log into ESPN Fantasy Football in your browser
2. Open Developer Tools (F12) → Network tab
3. Refresh the page and find any request to `fantasy.espn.com`
4. In the request headers, find:
   - `espn_s2`: Long cookie value
   - `SWID`: Value like `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`

**Note**: These cookies expire periodically, so you may need to update them.

### Environment Variables

All deployment methods support these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GMB_LEAGUE_ID` | Yes | Your ESPN league ID |
| `GMB_YEAR` | Yes | Fantasy season year |
| `GMB_ESPN_S2` | Private only | ESPN session cookie |
| `GMB_SWID` | Private only | ESPN user ID cookie |

## Development

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for package management
- Dependencies managed via `pyproject.toml` and `uv.lock`

### Quick Start

Run setup to create venv and install dependencies:
```bash
make setup
```

### Testing

Run tests with coverage:
```bash
uv run pytest --cov=src/gmb --cov-report=term-missing
```

See [TESTING.md](TESTING.md) for detailed testing information.

### Code Style

This project uses:
- **uv** for fast package management
- **Ruff** for code formatting and linting (100-column width)
- **Mypy** for type checking

Format code:
```bash
uv run ruff format .
```

Lint code:
```bash
uv run ruff check .
```

Type check:
```bash
uv run mypy src/gmb
```

See [FORMATTING.md](FORMATTING.md) for detailed formatting guidelines.

### Continuous Integration

GitHub Actions runs automated checks on every push:
- Tests with coverage reporting
- Ruff formatting and linting
- Mypy type checking

See [CI.md](CI.md) for CI/CD documentation.

## License

MIT License