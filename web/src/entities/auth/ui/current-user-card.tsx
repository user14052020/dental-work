"use client";

import { Avatar, Group, Stack, Text } from "@mantine/core";

import { useAuthSession } from "@/entities/auth/model/auth-session-context";

export function CurrentUserCard() {
  const { session } = useAuthSession();

  if (!session) {
    return null;
  }

  return (
    <Group gap="sm" wrap="nowrap">
      <Avatar color="teal" radius="xl">
        {session.user.email.slice(0, 1).toUpperCase()}
      </Avatar>
      <Stack gap={0}>
        <Text fw={700} size="sm">
          {session.user.email}
        </Text>
        <Text c="dimmed" size="xs">
          Администратор лаборатории
        </Text>
      </Stack>
    </Group>
  );
}
