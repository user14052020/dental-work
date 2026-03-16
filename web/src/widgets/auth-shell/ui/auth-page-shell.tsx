import { Card, Group, SimpleGrid, Stack, Text, Title } from "@mantine/core";
import { PropsWithChildren } from "react";

import { AppLogo } from "@/shared/ui/app-logo";

type AuthPageShellProps = PropsWithChildren<{
  title: string;
  description: string;
}>;

export function AuthPageShell({ title, description, children }: AuthPageShellProps) {
  return (
    <div className="min-h-screen app-shell-bg px-4 py-8 md:px-8 lg:px-10">
      <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="xl" className="mx-auto max-w-7xl">
        <Card className="panel-surface flex min-h-[440px] items-center justify-center p-8 md:p-12">
          <Stack gap="xl" maw={460}>
            <AppLogo />
            <Stack gap="md">
              <Title order={1} size="h1">
                Премиальный веб-кабинет для зуботехнической лаборатории.
              </Title>
              <Text c="dimmed" size="lg">
                Управляйте клиентами, исполнителями, материалами и заказами из браузера с единой серверной
                архитектурой и полнотекстовым поиском.
              </Text>
            </Stack>
            <Group gap="sm">
              <div className="rounded-full bg-white/70 px-4 py-2 text-sm font-medium text-slate-600">
                Next.js 15
              </div>
              <div className="rounded-full bg-white/70 px-4 py-2 text-sm font-medium text-slate-600">
                Mantine + Tailwind
              </div>
              <div className="rounded-full bg-white/70 px-4 py-2 text-sm font-medium text-slate-600">
                FSD
              </div>
            </Group>
          </Stack>
        </Card>

        <Card className="panel-surface p-8 md:p-12">
          <Stack gap="lg">
            <Stack gap={4}>
              <Title order={2}>{title}</Title>
              <Text c="dimmed">{description}</Text>
            </Stack>
            {children}
          </Stack>
        </Card>
      </SimpleGrid>
    </div>
  );
}
