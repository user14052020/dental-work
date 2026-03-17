import { NextRequest, NextResponse } from "next/server";

import {
  accessTokenCookieName,
  applyAuthCookies,
  clearAuthCookies,
  refreshTokenCookieName
} from "@/shared/server/auth/auth-cookies";
import {
  BackendAuthSession,
  createErrorResponse,
  isUnauthorizedError,
  refreshBackendSession
} from "@/shared/server/auth/auth-session";
import { fetchBackend } from "@/shared/server/backend/backend-client";

function getProxiedPath(pathname: string) {
  return pathname.replace(/^\/api\/proxy/, "");
}

function buildResponse(response: Response, body: BodyInit | null, refreshedSession?: BackendAuthSession | null) {
  const nextResponse = new NextResponse(body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/json",
      ...(response.headers.get("content-disposition")
        ? { "Content-Disposition": response.headers.get("content-disposition") as string }
        : {})
    }
  });

  if (refreshedSession) {
    applyAuthCookies(nextResponse, refreshedSession);
  }

  if (response.status === 401) {
    clearAuthCookies(nextResponse);
  }

  return nextResponse;
}

async function performAuthorizedRequest(
  request: NextRequest,
  accessToken: string | null,
  body: BodyInit | undefined
) {
  return fetchBackend({
    path: getProxiedPath(request.nextUrl.pathname),
    method: request.method,
    token: accessToken,
    body,
    contentType: request.headers.get("content-type"),
    search: request.nextUrl.search
  });
}

async function handleProxyRequest(request: NextRequest) {
  const accessToken = request.cookies.get(accessTokenCookieName)?.value ?? null;
  const refreshToken = request.cookies.get(refreshTokenCookieName)?.value ?? null;
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : Buffer.from(await request.arrayBuffer());

  let refreshedSession: BackendAuthSession | null = null;
  let currentAccessToken = accessToken;

  if (!currentAccessToken && refreshToken) {
    refreshedSession = await refreshBackendSession(refreshToken);
    currentAccessToken = refreshedSession.accessToken;
  }

  let response = await performAuthorizedRequest(request, currentAccessToken, body);

  if (response.status === 401 && refreshToken) {
    refreshedSession = await refreshBackendSession(refreshToken);
    response = await performAuthorizedRequest(request, refreshedSession.accessToken, body);
  }

  const responseBody = response.status === 204 ? null : Buffer.from(await response.arrayBuffer());
  return buildResponse(response, responseBody, refreshedSession);
}

async function handle(request: NextRequest) {
  try {
    return await handleProxyRequest(request);
  } catch (error) {
    const response = createErrorResponse(error);

    if (isUnauthorizedError(error)) {
      clearAuthCookies(response);
    }

    return response;
  }
}

export async function GET(request: NextRequest) {
  return handle(request);
}

export async function POST(request: NextRequest) {
  return handle(request);
}

export async function PATCH(request: NextRequest) {
  return handle(request);
}

export async function PUT(request: NextRequest) {
  return handle(request);
}

export async function DELETE(request: NextRequest) {
  return handle(request);
}
