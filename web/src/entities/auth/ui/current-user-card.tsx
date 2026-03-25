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
      <Avatar color="teal" radius="xl" size={38}>
        {(session.user.full_name || session.user.email).slice(0, 1).toUpperCase()}
      </Avatar>
      <Stack gap={0} className="min-w-0">
        <Text fw={700} size="sm" className="max-w-[180px] truncate">
          {session.user.full_name}
        </Text>
        <Text c="dimmed" size="xs">
          {session.user.job_title ?? session.user.email}
        </Text>
      </Stack>
    </Group>
  );
}
