"use client";

import { AppShell, Burger, Button, Group, NavLink, ScrollArea, Stack, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconPlus } from "@tabler/icons-react";
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
      header={{ height: 88 }}
      navbar={{ width: 320, breakpoint: "md", collapsed: { mobile: !opened } }}
      padding="md"
      className="app-shell-bg min-h-screen"
    >
      <AppShell.Header className="border-b border-white/50 bg-white/70 backdrop-blur-xl">
        <Group h="100%" justify="space-between" px="lg">
          <Group gap="md">
            <Burger hiddenFrom="md" opened={opened} onClick={toggle} size="sm" />
            <AppLogo />
          </Group>

          <Group gap="sm">
            <Button component={Link} href="/works" leftSection={<IconPlus size={16} />} variant="light">
              Новая работа
            </Button>
            <CurrentUserCard />
            <SignOutButton />
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar className="border-r border-white/50 bg-white/65 backdrop-blur-xl p-4">
        <Stack h="100%" justify="space-between">
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

          <div className="rounded-[28px] border border-white/70 bg-white/80 p-4 shadow-soft">
            <Text fw={700}>Поиск по всем реквизитам</Text>
            <Text c="dimmed" mt={6} size="sm">
              Все рабочие разделы используют серверный поиск и индексацию по полному набору реквизитов.
            </Text>
          </div>
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main>
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-1 py-4">{children}</div>
      </AppShell.Main>
    </AppShell>
  );
}
