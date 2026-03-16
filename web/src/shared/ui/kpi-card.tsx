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
    <Card className={cn("panel-surface", "shadow-panel")} padding="xl">
      <Group justify="space-between" align="start">
        <Stack gap={6}>
          <Text c="dimmed" size="sm">
            {title}
          </Text>
          <Text fw={800} size="2rem">
            {value}
          </Text>
          <Text c="dimmed" size="sm">
            {hint}
          </Text>
        </Stack>
        <ThemeIcon size={52} radius="xl" color="teal" variant="light">
          {icon}
        </ThemeIcon>
      </Group>
    </Card>
  );
}
