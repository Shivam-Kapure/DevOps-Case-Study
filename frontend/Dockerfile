# ==============================================================================
# Enterprise Payment & Notification Engine - Frontend Dockerfile
# ==============================================================================
FROM nginx:alpine

# Remove default nginx configurations
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend static assets
COPY . /usr/share/nginx/html/

# Copy and setup entrypoint script for dynamic API URL injection
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Remove server scripts and build configs from static serving directory
RUN rm -f /usr/share/nginx/html/Dockerfile \
          /usr/share/nginx/html/nginx.conf \
          /usr/share/nginx/html/docker-entrypoint.sh \
          /usr/share/nginx/html/server.py

# Default environment variables
ENV BACKEND_API_URL=http://localhost:28081 \
    FRONTEND_PORT=28080

# Document exposed container port
EXPOSE 28080

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
