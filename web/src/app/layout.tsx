import "@/app/globals.css";

import { ColorSchemeScript } from "@mantine/core";
import { PropsWithChildren } from "react";

import { AppProviders } from "@/shared/providers/app-providers";

export const metadata = {
  title: "Зуботехническая лаборатория",
  description: "Веб-система управления зуботехнической лабораторией."
};

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="ru">
      <head>
        <ColorSchemeScript defaultColorScheme="light" />
      </head>
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
