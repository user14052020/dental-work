"use client";

import { AppShell, Burger, Group, NavLink, ScrollArea, Stack, Text } from "@mantine/core";
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
  const [opened, { toggle }] = useDisclosure(false);

  return (
    <AppShell
      header={{ height: { base: 148, md: 88 } }}
      navbar={{ width: { base: 296, md: 320 }, breakpoint: "md", collapsed: { mobile: !opened } }}
      padding="md"
      className="app-shell-bg min-h-screen"
    >
      <AppShell.Header className="relative z-30 border-b border-white/50 bg-white/70 backdrop-blur-xl">
        <Group
          h="100%"
          justify="space-between"
          px="lg"
          className="items-start gap-y-3 py-4 md:items-center md:py-0"
        >
          <Group gap="md">
            <Burger hiddenFrom="md" opened={opened} onClick={toggle} size="sm" />
            <AppLogo />
          </Group>

          <Group gap="sm" wrap="wrap" justify="flex-end" className="min-w-0">
            <CurrentUserCard />
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

            <div className="rounded-[24px] border border-white/70 bg-white/80 p-4 shadow-soft">
              <Text fw={700}>Поиск по всем реквизитам</Text>
              <Text c="dimmed" mt={6} size="sm">
                Все рабочие разделы используют серверный поиск и индексацию по полному набору реквизитов.
              </Text>
            </div>

            <div className="mt-auto">
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
