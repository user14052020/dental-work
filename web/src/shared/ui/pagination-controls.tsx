import { Group, Pagination, Text } from "@mantine/core";

import { PageMeta } from "@/shared/types/api";

type PaginationControlsProps = {
  meta?: PageMeta;
  onChange: (page: number) => void;
};

export function PaginationControls({ meta, onChange }: PaginationControlsProps) {
  if (!meta) {
    return null;
  }

  return (
    <Group justify="space-between">
      <Text c="dimmed" size="sm">
        Всего записей: {meta.total_items}
      </Text>
      <Pagination total={meta.total_pages} value={meta.page} onChange={onChange} radius="xl" />
    </Group>
  );
}
