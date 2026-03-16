"use client";

import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from "react";

import { getMe } from "@/entities/auth/api/auth-api";
import {
  clearPersistedSession,
  persistSession,
  readStoredSession
} from "@/entities/auth/model/auth-storage";
import { AuthSession } from "@/entities/auth/model/types";

type AuthSessionContextValue = {
  session: AuthSession | null;
  isReady: boolean;
  applySession: (session: AuthSession) => void;
  clearSession: () => void;
};

const AuthSessionContext = createContext<AuthSessionContextValue | null>(null);

export function AuthSessionProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const initialSession = readStoredSession();

    if (initialSession) {
      setSession(initialSession);
      setIsReady(true);
      return;
    }

    getMe()
      .then((resolvedSession) => {
        persistSession(resolvedSession);
        setSession(resolvedSession);
      })
      .catch(() => {
        clearPersistedSession();
        setSession(null);
      })
      .finally(() => {
        setIsReady(true);
      });
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearPersistedSession();
      setSession(null);
      window.location.assign("/login");
    };

    window.addEventListener("dl:unauthorized", handleUnauthorized);

    return () => {
      window.removeEventListener("dl:unauthorized", handleUnauthorized);
    };
  }, []);

  const value = useMemo<AuthSessionContextValue>(
    () => ({
      session,
      isReady,
      applySession(nextSession) {
        persistSession(nextSession);
        setSession(nextSession);
      },
      clearSession() {
        clearPersistedSession();
        setSession(null);
      }
    }),
    [isReady, session]
  );

  return <AuthSessionContext.Provider value={value}>{children}</AuthSessionContext.Provider>;
}

export function useAuthSession() {
  const context = useContext(AuthSessionContext);

  if (!context) {
    throw new Error("useAuthSession must be used within AuthSessionProvider");
  }

  return context;
}
