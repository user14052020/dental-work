import { NextResponse } from "next/server";

import { AuthSession, AuthUser, LoginPayload, RegisterPayload } from "@/entities/auth/model/types";
import { fetchBackend } from "@/shared/server/backend/backend-client";
import { ApiErrorShape } from "@/shared/types/api";

export type BackendAuthSession = {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  user: AuthUser;
};

type ErrorResponsePayload = ApiErrorShape & {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
    request_id?: string;
    timestamp?: string;
  };
};

export class BackendApiError extends Error {
  status: number;
  payload: ErrorResponsePayload | null;

  constructor(status: number, payload: ErrorResponsePayload | null, fallbackMessage: string) {
    super(payload?.error?.message ?? fallbackMessage);
    this.name = "BackendApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function parseBackendPayload<T>(response: Response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  return JSON.parse(text) as T;
}

async function expectJsonResponse<T>(response: Response, fallbackMessage: string) {
  const payload = await parseBackendPayload<T | ErrorResponsePayload>(response);

  if (!response.ok) {
    throw new BackendApiError(response.status, payload as ErrorResponsePayload | null, fallbackMessage);
  }

  return payload as T;
}

export function toSessionSnapshot(session: BackendAuthSession | { user: AuthUser }): AuthSession {
  return { user: session.user };
}

export async function requestBackendSession(path: "/auth/login" | "/auth/register", body: LoginPayload | RegisterPayload) {
  const response = await fetchBackend({
    path,
    method: "POST",
    body: JSON.stringify(body),
    contentType: "application/json"
  });

  return expectJsonResponse<BackendAuthSession>(response, "Authentication request failed.");
}

export async function refreshBackendSession(refreshToken: string) {
  const response = await fetchBackend({
    path: "/auth/refresh",
    method: "POST",
    body: JSON.stringify({ refreshToken }),
    contentType: "application/json"
  });

  return expectJsonResponse<BackendAuthSession>(response, "Refresh token is invalid.");
}

export async function requestCurrentUser(accessToken: string) {
  const response = await fetchBackend({
    path: "/auth/me",
    token: accessToken
  });

  return expectJsonResponse<AuthUser>(response, "Unable to resolve the current user.");
}

export async function revokeBackendSession(refreshToken: string) {
  await fetchBackend({
    path: "/auth/logout",
    method: "POST",
    body: JSON.stringify({ refreshToken }),
    contentType: "application/json"
  });
}

export function isUnauthorizedError(error: unknown) {
  return error instanceof BackendApiError && error.status === 401;
}

export function createErrorResponse(error: unknown) {
  if (error instanceof BackendApiError) {
    return NextResponse.json(
      error.payload ?? {
        error: {
          code: "backend_error",
          message: error.message
        }
      },
      { status: error.status }
    );
  }

  return NextResponse.json(
    {
      error: {
        code: "internal_error",
        message: "Внутренняя ошибка сервера."
      }
    },
    { status: 500 }
  );
}
