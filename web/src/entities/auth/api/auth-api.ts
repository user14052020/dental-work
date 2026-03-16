import { httpClient } from "@/shared/api/http-client";

import { AuthSession, LoginPayload, RegisterPayload } from "../model/types";

export function login(payload: LoginPayload) {
  return httpClient<AuthSession>({
    path: "/api/auth/login",
    method: "POST",
    body: payload
  });
}

export function register(payload: RegisterPayload) {
  return httpClient<AuthSession>({
    path: "/api/auth/register",
    method: "POST",
    body: payload
  });
}

export function getMe() {
  return httpClient<AuthSession>({
    path: "/api/auth/me"
  });
}

export function logout() {
  return httpClient<void>({
    path: "/api/auth/logout",
    method: "POST"
  });
}
