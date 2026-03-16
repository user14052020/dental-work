const path = require("path");

const rootDir = process.env.DENTAL_LAB_ROOT || "/opt/dental-work";
const pm2HomeDir = process.env.PM2_HOME || path.join(rootDir, ".pm2");
const logsDir = path.join(pm2HomeDir, "logs");

module.exports = {
  apps: [
    {
      name: "dental-lab-backend",
      cwd: rootDir,
      script: path.join(rootDir, "backend", ".venv", "bin", "uvicorn"),
      args: "app.main:app --app-dir backend --host 127.0.0.1 --port 8100",
      interpreter: "none",
      env: {
        PYTHONPATH: "backend"
      },
      out_file: path.join(logsDir, "dental-lab-backend-out.log"),
      error_file: path.join(logsDir, "dental-lab-backend-error.log"),
      time: true
    },
    {
      name: "dental-lab-web",
      cwd: path.join(rootDir, "web"),
      script: "npm",
      args: "run start -- --hostname 0.0.0.0 --port 3100",
      interpreter: "none",
      env: {
        AUTH_COOKIE_SECURE: "false",
        NEXT_PUBLIC_API_URL: "http://127.0.0.1:8100/api/v1",
        INTERNAL_API_URL: "http://127.0.0.1:8100/api/v1"
      },
      out_file: path.join(logsDir, "dental-lab-web-out.log"),
      error_file: path.join(logsDir, "dental-lab-web-error.log"),
      time: true
    }
  ]
};
