import { SimpleGrid, Stack, Text } from "@mantine/core";

type DetailItem = {
  label: string;
  value: string;
};

type DetailGridProps = {
  items: DetailItem[];
};

export function DetailGrid({ items }: DetailGridProps) {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="lg">
      {items.map((item) => (
        <Stack key={item.label} gap={4}>
          <Text c="dimmed" size="sm">
            {item.label}
          </Text>
          <Text fw={600}>{item.value}</Text>
        </Stack>
      ))}
    </SimpleGrid>
  );
}
