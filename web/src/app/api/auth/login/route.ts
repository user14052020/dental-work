import { NextRequest, NextResponse } from "next/server";

import { applyAuthCookies } from "@/shared/server/auth/auth-cookies";
import { createErrorResponse, requestBackendSession, toSessionSnapshot } from "@/shared/server/auth/auth-session";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const session = await requestBackendSession("/auth/login", payload);
    const response = NextResponse.json(toSessionSnapshot(session));

    applyAuthCookies(response, session);

    return response;
  } catch (error) {
    return createErrorResponse(error);
  }
}
