"use client";

import { AppShell, Burger, Group, NavLink, ScrollArea, Stack } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import Link from "next/link";
import { PropsWithChildren } from "react";

import { CurrentUserCard } from "@/entities/auth/ui/current-user-card";
import { SignOutButton } from "@/features/auth/sign-out/ui/sign-out-button";
import { navigationItems } from "@/shared/config/navigation";
import { AppLogo } from "@/shared/ui/app-logo";
import { usePathname } from "next/navigation";

export function AppShellLayout({ children }: PropsWithChildren) {
  const pathname = usePathname();
  const [opened, { toggle, close }] = useDisclosure(false);

  return (
    <AppShell
      header={{ height: { base: 84, md: 88 } }}
      navbar={{ width: { base: 296, md: 320 }, breakpoint: "md", collapsed: { mobile: !opened } }}
      padding="md"
      className="app-shell-bg min-h-screen"
    >
      <AppShell.Header className="relative z-30 border-b border-white/50 bg-white/70 backdrop-blur-xl">
        <Group h="100%" justify="flex-start" px="lg" className="min-w-0 items-center">
          <Group gap="md" wrap="nowrap" className="min-w-0">
            <Burger hiddenFrom="md" opened={opened} onClick={toggle} size="sm" />
            <AppLogo />
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar className="relative z-20 border-r border-white/50 bg-white/65 p-3 md:p-4 backdrop-blur-xl">
        <Stack h="100%" justify="space-between">
          <Stack gap="md" h="100%">
            <ScrollArea offsetScrollbars>
              <Stack gap="xs">
                {navigationItems.map((item) => (
                  <NavLink
                    key={item.href}
                    component={Link}
                    href={item.href}
                    onClick={close}
                    active={pathname === item.href}
                    label={item.label}
                    description={item.description}
                    leftSection={<item.icon size={18} />}
                    variant="filled"
                    styles={{
                      root: {
                        borderRadius: 18
                      }
                    }}
                  />
                ))}
              </Stack>
            </ScrollArea>

            <div className="mt-auto">
              <div className="mb-3 rounded-[22px] border border-white/70 bg-white/80 p-3 shadow-soft">
                <CurrentUserCard />
              </div>
              <SignOutButton fullWidth />
            </div>
          </Stack>
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main className="relative z-0 min-w-0">
        <div className="mx-auto flex w-full max-w-7xl min-w-0 flex-col gap-6 overflow-x-hidden px-1 py-4">
          {children}
        </div>
      </AppShell.Main>
    </AppShell>
  );
}
