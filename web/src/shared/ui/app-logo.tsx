import { Badge, Group, Stack, Text, ThemeIcon } from "@mantine/core";
import { IconDental } from "@tabler/icons-react";

export function AppLogo() {
  return (
    <Group gap="md" wrap="nowrap" className="min-w-0 gap-3 md:gap-4">
      <ThemeIcon size={40} radius="xl" color="teal" variant="light" className="md:h-12 md:w-12">
        <IconDental size={20} className="md:h-6 md:w-6" />
      </ThemeIcon>

      <Stack gap={2} className="min-w-0">
        <Group gap="xs">
          <Text fw={800} size="lg" className="truncate text-[1.05rem] md:text-[1.125rem]">
            Кабинет лаборатории
          </Text>
          <Badge radius="xl" variant="light" color="teal" size="sm" className="text-[0.65rem] lowercase">
            web
          </Badge>
        </Group>
        <Text c="dimmed" size="sm" className="hidden sm:block">
          Операционный кабинет лаборатории
        </Text>
      </Stack>
    </Group>
  );
}
