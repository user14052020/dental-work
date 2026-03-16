import { NextResponse } from "next/server";

import { BackendAuthSession } from "@/shared/server/auth/auth-session";

export const accessTokenCookieName = "dl_access_token";
export const refreshTokenCookieName = "dl_refresh_token";

function isSecureCookie() {
  if (process.env.AUTH_COOKIE_SECURE) {
    return process.env.AUTH_COOKIE_SECURE === "true";
  }

  return process.env.NODE_ENV === "production";
}

function getCookieMaxAge(token: string) {
  const [, payloadSegment] = token.split(".");

  if (!payloadSegment) {
    return undefined;
  }

  try {
    const payload = JSON.parse(Buffer.from(payloadSegment, "base64url").toString("utf-8")) as {
      exp?: number;
    };

    if (!payload.exp) {
      return undefined;
    }

    const maxAge = payload.exp - Math.floor(Date.now() / 1000);
    return maxAge > 0 ? maxAge : undefined;
  } catch {
    return undefined;
  }
}

export function applyAuthCookies(response: NextResponse, session: BackendAuthSession) {
  response.cookies.set(accessTokenCookieName, session.accessToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: isSecureCookie(),
    path: "/",
    maxAge: getCookieMaxAge(session.accessToken)
  });
  response.cookies.set(refreshTokenCookieName, session.refreshToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: isSecureCookie(),
    path: "/",
    maxAge: getCookieMaxAge(session.refreshToken)
  });
}

export function clearAuthCookies(response: NextResponse) {
  response.cookies.set(accessTokenCookieName, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: isSecureCookie(),
    path: "/",
    maxAge: 0
  });
  response.cookies.set(refreshTokenCookieName, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: isSecureCookie(),
    path: "/",
    maxAge: 0
  });
}
