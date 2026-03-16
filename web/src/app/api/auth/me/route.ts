import { NextRequest, NextResponse } from "next/server";

import {
  accessTokenCookieName,
  applyAuthCookies,
  clearAuthCookies,
  refreshTokenCookieName
} from "@/shared/server/auth/auth-cookies";
import {
  createErrorResponse,
  isUnauthorizedError,
  refreshBackendSession,
  requestCurrentUser,
  toSessionSnapshot
} from "@/shared/server/auth/auth-session";

export async function GET(request: NextRequest) {
  const accessToken = request.cookies.get(accessTokenCookieName)?.value;
  const refreshToken = request.cookies.get(refreshTokenCookieName)?.value;

  if (!accessToken && !refreshToken) {
    return NextResponse.json(
        {
          error: {
            code: "authentication_failed",
            message: "Требуется авторизация."
          }
        },
      { status: 401 }
    );
  }

  if (accessToken) {
    try {
      const user = await requestCurrentUser(accessToken);
      return NextResponse.json(toSessionSnapshot({ user }));
    } catch (error) {
      if (!refreshToken || !isUnauthorizedError(error)) {
        const response = createErrorResponse(error);

        if (isUnauthorizedError(error)) {
          clearAuthCookies(response);
        }

        return response;
      }
    }
  }

  try {
    const session = await refreshBackendSession(refreshToken!);
    const response = NextResponse.json(toSessionSnapshot(session));

    applyAuthCookies(response, session);

    return response;
  } catch (error) {
    const response = createErrorResponse(error);
    clearAuthCookies(response);
    return response;
  }
}
