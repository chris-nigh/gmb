#!/bin/bash
# Quick deployment setup script for GMB Dashboard

set -e

echo "========================================"
echo "GMB Dashboard Deployment Setup"
echo "========================================"
echo ""

# Check if running in git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository. Please run from project root."
    exit 1
fi

# Function to prompt for input with default
prompt_input() {
    local prompt="$1"
    local default="$2"
    local varname="$3"

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        input="${input:-$default}"
    else
        read -p "$prompt: " input
    fi

    eval "$varname='$input'"
}

echo "This script will help you set up deployment configuration."
echo ""

# Ask for deployment method
echo "Choose deployment method:"
echo "1) Streamlit Community Cloud (Free, easiest)"
echo "2) Docker / Docker Compose"
echo "3) Linux Server (systemd)"
echo "4) Just create .streamlit/secrets.toml for local testing"
echo ""
read -p "Enter choice [1-4]: " deploy_choice

# Collect ESPN credentials
echo ""
echo "Enter your ESPN Fantasy League details:"
prompt_input "League ID" "" LEAGUE_ID
prompt_input "Year" "2025" YEAR
echo ""
echo "For PRIVATE leagues, you need ESPN cookies."
echo "For PUBLIC leagues, press Enter to skip."
read -p "Is this a private league? (y/N): " is_private

if [[ "$is_private" =~ ^[Yy]$ ]]; then
    prompt_input "ESPN_S2 cookie" "" ESPN_S2
    prompt_input "SWID cookie" "" SWID
else
    ESPN_S2=""
    SWID=""
fi

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

case $deploy_choice in
    1)
        echo ""
        echo "Setting up for Streamlit Community Cloud..."
        echo ""
        echo "Next steps:"
        echo "1. Push your code to GitHub: git push"
        echo "2. Go to https://share.streamlit.io"
        echo "3. Click 'New app' and select your repository"
        echo "4. Set main file to: app.py"
        echo "5. In Advanced settings → Secrets, add:"
        echo ""
        echo "GMB_LEAGUE_ID = \"$LEAGUE_ID\""
        echo "GMB_YEAR = \"$YEAR\""
        if [ -n "$ESPN_S2" ]; then
            echo "GMB_ESPN_S2 = \"$ESPN_S2\""
            echo "GMB_SWID = \"$SWID\""
        fi
        echo ""
        ;;

    2)
        echo ""
        echo "Setting up Docker deployment..."

        # Create .env file for docker-compose
        cat > .env <<EOF
GMB_LEAGUE_ID=$LEAGUE_ID
GMB_YEAR=$YEAR
GMB_ESPN_S2=$ESPN_S2
GMB_SWID=$SWID
EOF

        echo "Created .env file for Docker Compose"
        echo ""
        echo "To deploy:"
        echo "  docker-compose up -d"
        echo ""
        echo "To view logs:"
        echo "  docker-compose logs -f"
        echo ""
        echo "To stop:"
        echo "  docker-compose down"
        ;;

    3)
        echo ""
        echo "Setting up systemd service..."

        # Create modified service file
        sed -e "s/your_league_id/$LEAGUE_ID/" \
            -e "s/2025/$YEAR/" \
            -e "s/your_espn_s2/$ESPN_S2/" \
            -e "s/your_swid/$SWID/" \
            deployment/gmb-dashboard.service > /tmp/gmb-dashboard.service

        echo "Modified service file created at: /tmp/gmb-dashboard.service"
        echo ""
        echo "To deploy:"
        echo "  sudo cp /tmp/gmb-dashboard.service /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable gmb-dashboard"
        echo "  sudo systemctl start gmb-dashboard"
        echo ""
        echo "To check status:"
        echo "  sudo systemctl status gmb-dashboard"
        ;;

    4)
        echo ""
        echo "Creating local secrets file..."
        ;;
esac

# Always create secrets.toml for local testing
cat > .streamlit/secrets.toml <<EOF
GMB_LEAGUE_ID = "$LEAGUE_ID"
GMB_YEAR = "$YEAR"
EOF

if [ -n "$ESPN_S2" ]; then
    cat >> .streamlit/secrets.toml <<EOF
GMB_ESPN_S2 = "$ESPN_S2"
GMB_SWID = "$SWID"
EOF
fi

echo ""
echo "Created .streamlit/secrets.toml for local testing"
echo ""
echo "You can now test locally with:"
echo "  streamlit run app.py"
echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
