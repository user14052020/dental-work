import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#132033",
        mist: "#edf4f7",
        tide: "#5e7b85",
        accent: "#1f8b85",
        accentSoft: "#d7f2ef",
        line: "#d9e6ea"
      },
      boxShadow: {
        panel: "0 22px 60px rgba(19, 32, 51, 0.08)",
        soft: "0 14px 40px rgba(19, 32, 51, 0.06)"
      },
      backgroundImage: {
        "shell-grid":
          "radial-gradient(circle at top left, rgba(31, 139, 133, 0.16), transparent 28%), radial-gradient(circle at bottom right, rgba(61, 103, 131, 0.12), transparent 24%)"
      }
    }
  },
  plugins: []
};

export default config;
