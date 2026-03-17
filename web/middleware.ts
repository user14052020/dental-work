import { NextRequest, NextResponse } from "next/server";

const authPages = new Set(["/login", "/register"]);
const publicPrefixes = ["/_next", "/favicon.ico"];
const accessTokenCookieName = "dl_access_token";
const refreshTokenCookieName = "dl_refresh_token";

function isPublicPath(pathname: string) {
  return publicPrefixes.some((prefix) => pathname.startsWith(prefix));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get(accessTokenCookieName)?.value;
  const refreshToken = request.cookies.get(refreshTokenCookieName)?.value;
  const hasSession = Boolean(accessToken || refreshToken);
  const isAuthPage = authPages.has(pathname);

  if (!hasSession && !isAuthPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasSession && isAuthPage) {
    return NextResponse.redirect(new URL("/works", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image).*)"]
};
