import { PropsWithChildren } from "react";

import { AppShellLayout } from "@/widgets/app-shell/ui/app-shell-layout";

export default function ProtectedLayout({ children }: PropsWithChildren) {
  return <AppShellLayout>{children}</AppShellLayout>;
}
