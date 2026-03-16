const path = require("path");

const rootDir = process.env.DENTAL_LAB_ROOT || "/opt/dental-work";
const backendBinDir = path.join(rootDir, "backend", ".venv", "bin");
const webDir = path.join(rootDir, "web");
const webNodeBinDir = path.join(webDir, "node_modules", ".bin");
const logsDir = path.join(rootDir, ".pm2", "logs");
const systemPath = process.env.PATH || "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin";

module.exports = {
  apps: [
    {
      name: "dental-lab-backend",
      cwd: rootDir,
      script: path.join(backendBinDir, "uvicorn"),
      args: "app.main:app --app-dir backend --host 127.0.0.1 --port 8100",
      interpreter: "none",
      env: {
        PYTHONPATH: "backend",
        PATH: `${backendBinDir}:${systemPath}`
      },
      out_file: path.join(logsDir, "dental-lab-backend-out.log"),
      error_file: path.join(logsDir, "dental-lab-backend-error.log"),
      time: true
    },
    {
      name: "dental-lab-web",
      cwd: webDir,
      script: path.join(webNodeBinDir, "next"),
      args: "start --hostname 0.0.0.0 --port 3100",
      interpreter: "none",
      env: {
        NODE_ENV: "production",
        AUTH_COOKIE_SECURE: "false",
        NEXT_PUBLIC_API_URL: "http://127.0.0.1:8100/api/v1",
        INTERNAL_API_URL: "http://127.0.0.1:8100/api/v1",
        PATH: `${webNodeBinDir}:${systemPath}`
      },
      out_file: path.join(logsDir, "dental-lab-web-out.log"),
      error_file: path.join(logsDir, "dental-lab-web-error.log"),
      time: true
    }
  ]
};
