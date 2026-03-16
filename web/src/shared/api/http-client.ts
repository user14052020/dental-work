import { appConfig } from "@/shared/config/app-config";
import { ApiErrorShape } from "@/shared/types/api";

type Primitive = string | number | boolean | null | undefined;

type RequestOptions = {
  path: string;
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  query?: Record<string, Primitive>;
};

function buildUrl(path: string, query?: Record<string, Primitive>) {
  const baseUrl =
    path.startsWith("/api/") || /^https?:\/\//.test(path)
      ? typeof window === "undefined"
        ? "http://localhost"
        : window.location.origin
      : appConfig.apiBaseUrl;
  const url = new URL(path, baseUrl);

  if (!query) {
    return url.toString();
  }

  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }

    url.searchParams.set(key, String(value));
  });

  return url.toString();
}

function readErrorMessage(payload: ApiErrorShape | null, fallback: string) {
  return payload?.error?.message ?? fallback;
}

function notifyUnauthorized() {
  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(new Event("dl:unauthorized"));
}

export class ApiError extends Error {
  status: number;
  code?: string;
  details?: Record<string, unknown>;

  constructor(message: string, status: number, code?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function httpClient<TResponse>({
  path,
  method = "GET",
  body,
  query
}: RequestOptions): Promise<TResponse> {
  const response = await fetch(buildUrl(path, query), {
    method,
    headers: {
      "Content-Type": "application/json"
    },
    body: body ? JSON.stringify(body) : undefined
  });

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as ApiErrorShape | TResponse) : null;

  if (!response.ok) {
    const errorPayload = payload as ApiErrorShape | null;

    if (response.status === 401 && !path.startsWith("/api/auth/")) {
      notifyUnauthorized();
    }

    throw new ApiError(
      readErrorMessage(errorPayload, "Непредвиденная ошибка API."),
      response.status,
      errorPayload?.error?.code,
      errorPayload?.error?.details
    );
  }

  return payload as TResponse;
}
