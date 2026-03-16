const fallbackApiBaseUrl = "http://localhost:8100/api/v1";

export const appConfig = {
  apiBaseUrl: (process.env.NEXT_PUBLIC_API_URL ?? fallbackApiBaseUrl).replace(/\/$/, ""),
  appName: "Зуботехническая лаборатория"
};
