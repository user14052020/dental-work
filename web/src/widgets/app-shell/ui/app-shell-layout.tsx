"use client";

import { AppShell, Burger, Button, Group, Menu, NavLink, ScrollArea, Stack } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import Link from "next/link";
import { PropsWithChildren, useEffect, useState } from "react";

import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { CurrentUserCard } from "@/entities/auth/ui/current-user-card";
import { SignOutButton } from "@/features/auth/sign-out/ui/sign-out-button";
import { headerNavigationMenus, sidebarNavigationItems } from "@/shared/config/navigation";
import { hasAnyPermission } from "@/shared/lib/auth/permissions";
import { AppLogo } from "@/shared/ui/app-logo";
import { usePathname } from "next/navigation";

function isRouteActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShellLayout({ children }: PropsWithChildren) {
  const pathname = usePathname() ?? "";
  const [opened, { toggle, close }] = useDisclosure(false);
  const [openedHeaderMenu, setOpenedHeaderMenu] = useState<string | null>(null);
  const { isReady, session } = useAuthSession();
  const visibleSidebarItems = !isReady
    ? sidebarNavigationItems
    : sidebarNavigationItems.filter((item) => hasAnyPermission(session?.user.permission_codes, item.requiredPermissions));
  const visibleHeaderMenus = !isReady
    ? headerNavigationMenus
    : headerNavigationMenus
        .map((menu) => ({
          ...menu,
          items: menu.items.filter((item) => hasAnyPermission(session?.user.permission_codes, item.requiredPermissions))
        }))
        .filter((menu) => menu.items.length > 0);

  useEffect(() => {
    setOpenedHeaderMenu(null);
  }, [pathname]);

  return (
    <AppShell
      header={{ height: { base: 124, md: 88 } }}
      navbar={{ width: { base: 296, md: 320 }, breakpoint: "md", collapsed: { mobile: !opened } }}
      padding="md"
      className="app-shell-bg min-h-screen"
    >
      <AppShell.Header className="relative z-30 border-b border-white/50 bg-white/70 backdrop-blur-xl">
        <div className="flex h-full flex-col justify-center gap-3 px-4 md:flex-row md:items-center md:justify-between md:px-6">
          <Group justify="space-between" wrap="nowrap" className="min-w-0 md:flex-1">
            <Group gap="md" wrap="nowrap" className="min-w-0">
              <Burger hiddenFrom="md" opened={opened} onClick={toggle} size="sm" />
              <AppLogo />
            </Group>
          </Group>

          {visibleHeaderMenus.length > 0 ? (
            <div className="w-full md:w-auto">
              <Group gap="xs" wrap="wrap" className="md:justify-end">
                {visibleHeaderMenus.map((menu) => {
                  const menuActive = menu.items.some((item) => isRouteActive(pathname, item.href));

                  return (
                    <Menu
                      key={menu.label}
                      shadow="lg"
                      width={320}
                      position="bottom-start"
                      opened={openedHeaderMenu === menu.label}
                      onChange={(nextOpened) => setOpenedHeaderMenu(nextOpened ? menu.label : null)}
                    >
                      <Menu.Target>
                        <Button
                          variant={menuActive ? "light" : "subtle"}
                          color={menuActive ? "blue" : "gray"}
                          radius="xl"
                          size="xs"
                          leftSection={<menu.icon size={16} />}
                          className="whitespace-nowrap"
                        >
                          {menu.label}
                        </Button>
                      </Menu.Target>

                      <Menu.Dropdown className="min-w-[280px]">
                        <Stack gap="xs" p="xs">
                          {menu.items.map((item) => (
                            <NavLink
                              key={item.href}
                              component={Link}
                              href={item.href}
                              onClick={() => {
                                setOpenedHeaderMenu(null);
                                close();
                              }}
                              active={isRouteActive(pathname, item.href)}
                              label={item.label}
                              description={item.description}
                              leftSection={<item.icon size={18} />}
                              variant="filled"
                              styles={{
                                root: {
                                  borderRadius: 16
                                }
                              }}
                            />
                          ))}
                        </Stack>
                      </Menu.Dropdown>
                    </Menu>
                  );
                })}
              </Group>
            </div>
          ) : null}
        </div>
      </AppShell.Header>

      <AppShell.Navbar className="relative z-20 border-r border-white/50 bg-white/65 p-3 md:p-4 backdrop-blur-xl">
        <Stack h="100%" justify="space-between">
          <Stack gap="md" h="100%">
            <ScrollArea offsetScrollbars>
              <Stack gap="xs">
                {visibleSidebarItems.map((item) => (
                  <NavLink
                    key={item.href}
                    component={Link}
                    href={item.href}
                    onClick={close}
                    active={isRouteActive(pathname, item.href)}
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
