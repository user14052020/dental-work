"use client";

import { Avatar, Group, Stack, Text } from "@mantine/core";

import { useAuthSession } from "@/entities/auth/model/auth-session-context";

export function CurrentUserCard() {
  const { session } = useAuthSession();

  if (!session) {
    return null;
  }

  return (
    <Group gap="sm" wrap="nowrap" className="min-w-0">
      <Avatar color="teal" radius="xl">
        {session.user.email.slice(0, 1).toUpperCase()}
      </Avatar>
      <Stack gap={0} className="min-w-0">
        <Text fw={700} size="sm" className="max-w-[148px] truncate md:max-w-none">
          {session.user.email}
        </Text>
        <Text c="dimmed" size="xs" className="hidden md:block">
          Администратор лаборатории
        </Text>
      </Stack>
    </Group>
  );
}
