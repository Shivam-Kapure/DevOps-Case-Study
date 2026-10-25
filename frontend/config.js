/**
 * Enterprise Payment & Notification Engine - Frontend Runtime Configuration
 * 
 * Note: You can change the backend URL here, via the in-app "Settings" button,
 * or by setting the BACKEND_API_URL environment variable when running via Docker/server.py.
 */
window.__APP_CONFIG__ = {
  // Configurable Backend API URL (Default verified port: 28081)
  backendApiUrl: window.localStorage.getItem('API_URL_OVERRIDE') || "http://localhost:28081",
  
  // Dashboard polling and metadata
  refreshIntervalMs: 30000,
  defaultFrontendPort: 28080,
  kubernetesNodePort: 30099,
  version: "1.0.0",
  appName: "Enterprise Payment & Notification Engine"
};
