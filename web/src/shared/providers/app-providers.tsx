"use client";

import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClientProvider } from "@tanstack/react-query";
import { PropsWithChildren, useState } from "react";

import { AuthSessionProvider } from "@/entities/auth/model/auth-session-context";
import { createQueryClient } from "@/shared/api/query-client";
import { mantineTheme } from "@/shared/providers/mantine-theme";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(createQueryClient);

  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider theme={mantineTheme} defaultColorScheme="auto">
        <AuthSessionProvider>
          <Notifications position="top-right" />
          {children}
        </AuthSessionProvider>
      </MantineProvider>
    </QueryClientProvider>
  );
}
