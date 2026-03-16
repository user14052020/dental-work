import { AuthSession } from "@/entities/auth/model/types";

export function readStoredSession(): AuthSession | null {
  return null;
}

export function persistSession(_session: AuthSession) {
  return undefined;
}

export function clearPersistedSession() {
  return undefined;
}
