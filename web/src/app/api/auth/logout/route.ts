import { NextRequest, NextResponse } from "next/server";

import { clearAuthCookies, refreshTokenCookieName } from "@/shared/server/auth/auth-cookies";
import { revokeBackendSession } from "@/shared/server/auth/auth-session";

export async function POST(request: NextRequest) {
  const refreshToken = request.cookies.get(refreshTokenCookieName)?.value;
  const response = new NextResponse(null, { status: 204 });

  if (refreshToken) {
    await revokeBackendSession(refreshToken);
  }

  clearAuthCookies(response);

  return response;
}
