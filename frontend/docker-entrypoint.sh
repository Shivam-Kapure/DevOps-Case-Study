#!/bin/sh
set -e

# Replace config.js with container BACKEND_API_URL environment variable if set
if [ -n "$BACKEND_API_URL" ]; then
  cat <<EOF > /usr/share/nginx/html/config.js
window.__APP_CONFIG__ = {
  backendApiUrl: "$BACKEND_API_URL",
  refreshIntervalMs: 30000,
  defaultFrontendPort: 28080,
  kubernetesNodePort: 30099,
  version: "1.0.0",
  appName: "Enterprise Payment & Notification Engine"
};
EOF
fi

# Also generate config.json for dynamic runtime fetch
if [ -n "$BACKEND_API_URL" ]; then
  cat <<EOF > /usr/share/nginx/html/config.json
{
  "backendApiUrl": "$BACKEND_API_URL",
  "frontendPort": 28080,
  "environment": "${APP_ENV:-production}",
  "status": "ready"
}
EOF
fi

exec "$@"
