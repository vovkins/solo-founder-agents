#!/bin/bash
# Deploy script for solo-founder-agents
# Usage: ./deploy.sh

set -e
cd ~/projects/solo-founder-agents

echo "=== 1. Stop containers ==="
docker compose --profile bot down

echo "=== 2. Remove old images ==="
docker rmi solo-founder-agents-app solo-founder-agents-telegram-bot -f 2>/dev/null || true

echo "=== 3. Pull latest code ==="
git pull origin main

echo "=== 4. Build fresh images ==="
docker compose --profile bot build --no-cache

echo "=== 5. Start containers ==="
docker compose --profile bot up -d

sleep 5

echo "=== 6. Verify bot is running ==="
docker logs sfa-telegram --tail 5

echo ""
echo "✅ Deploy complete!"
