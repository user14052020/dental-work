import { Group, Stack, Text, Title } from "@mantine/core";
import { PropsWithChildren, ReactNode } from "react";

type PageHeadingProps = PropsWithChildren<{
  title: string;
  description: string;
  actions?: ReactNode;
}>;

export function PageHeading({ title, description, actions, children }: PageHeadingProps) {
  return (
    <Stack gap="lg">
      <Group justify="space-between" align="end">
        <Stack gap={4}>
          <Title order={1} size="h2">
            {title}
          </Title>
          <Text c="dimmed" maw={720}>
            {description}
          </Text>
        </Stack>
        {actions}
      </Group>
      {children}
    </Stack>
  );
}
