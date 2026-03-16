import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit, IconEye } from "@tabler/icons-react";

import { Executor } from "@/entities/executors/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type ExecutorsTableProps = {
  items: Executor[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (executor: Executor) => void;
  onEdit: (executor: Executor) => void;
};

export function ExecutorsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView,
  onEdit
}: ExecutorsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={920}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Исполнитель</Table.Th>
                  <Table.Th>Специализация</Table.Th>
                  <Table.Th>Ставка</Table.Th>
                  <Table.Th>Работ</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((executor) => (
                  <Table.Tr key={executor.id}>
                    <Table.Td>
                      <Text fw={700}>{executor.full_name}</Text>
                      <Text c="dimmed" size="sm">
                        {executor.email ?? executor.phone ?? "Контакты не указаны"}
                      </Text>
                    </Table.Td>
                    <Table.Td>{executor.specialization ?? "—"}</Table.Td>
                    <Table.Td>{formatCurrency(executor.hourly_rate)}</Table.Td>
                    <Table.Td>{executor.work_count}</Table.Td>
                    <Table.Td>
                      <StatusPill kind="boolean" value={executor.is_active} />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(executor)}>
                          <IconEye size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" onClick={() => onEdit(executor)}>
                          <IconEdit size={16} />
                        </ActionIcon>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
          <PaginationControls meta={meta} onChange={onPageChange} />
        </>
      ) : (
        <Text c="dimmed">Исполнители не найдены.</Text>
      )}
    </SectionCard>
  );
}
