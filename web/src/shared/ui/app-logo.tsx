import { Badge, Group, Stack, Text, ThemeIcon } from "@mantine/core";
import { IconDental } from "@tabler/icons-react";

export function AppLogo() {
  return (
    <Group gap="md" wrap="nowrap">
      <ThemeIcon size={48} radius="xl" color="teal" variant="light">
        <IconDental size={24} />
      </ThemeIcon>

      <Stack gap={2}>
        <Group gap="xs">
          <Text fw={800} size="lg">
            Кабинет лаборатории
          </Text>
          <Badge radius="xl" variant="light" color="teal">
            Веб
          </Badge>
        </Group>
        <Text c="dimmed" size="sm">
          Операционный кабинет лаборатории
        </Text>
      </Stack>
    </Group>
  );
}
