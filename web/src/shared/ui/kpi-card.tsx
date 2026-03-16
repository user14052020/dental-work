import { Card, Group, Stack, Text, ThemeIcon } from "@mantine/core";
import { ReactNode } from "react";

import { cn } from "@/shared/lib/cn";

type KpiCardProps = {
  title: string;
  value: string;
  hint: string;
  icon: ReactNode;
};

export function KpiCard({ title, value, hint, icon }: KpiCardProps) {
  return (
    <Card className={cn("panel-surface", "shadow-panel", "h-full rounded-[30px]")} padding={0}>
      <div className="flex h-full flex-col p-5 md:p-6">
        <Group justify="space-between" align="start" wrap="nowrap" className="h-full gap-4">
          <Stack gap={6} className="min-w-0 flex-1">
            <Text c="dimmed" size="sm">
              {title}
            </Text>
            <Text fw={800} component="div" className="text-[2rem] leading-none md:text-[2.5rem]">
              {value}
            </Text>
            <Text c="dimmed" size="sm" className="max-w-[18rem]">
              {hint}
            </Text>
          </Stack>
          <ThemeIcon size={50} radius="xl" color="teal" variant="light" className="shrink-0">
            {icon}
          </ThemeIcon>
        </Group>
      </div>
    </Card>
  );
}
