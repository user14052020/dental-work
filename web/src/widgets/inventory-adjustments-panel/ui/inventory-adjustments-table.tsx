import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEye } from "@tabler/icons-react";

import { InventoryAdjustmentCompact } from "@/entities/inventory-adjustments/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";

type InventoryAdjustmentsTableProps = {
  items: InventoryAdjustmentCompact[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (adjustment: InventoryAdjustmentCompact) => void;
};

export function InventoryAdjustmentsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView
}: InventoryAdjustmentsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1080}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Инвентаризация</Table.Th>
                  <Table.Th>Позиций</Table.Th>
                  <Table.Th>Изменено</Table.Th>
                  <Table.Th>Прибавка</Table.Th>
                  <Table.Th>Списание</Table.Th>
                  <Table.Th>Влияние на стоимость</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((adjustment) => (
                  <Table.Tr key={adjustment.id}>
                    <Table.Td>
                      <Text fw={700}>{adjustment.adjustment_number}</Text>
                      <Text c="dimmed" size="sm">
                        {formatDateTime(adjustment.recorded_at)}
                      </Text>
                    </Table.Td>
                    <Table.Td>{adjustment.items_count}</Table.Td>
                    <Table.Td>{adjustment.changed_items_count}</Table.Td>
                    <Table.Td>{adjustment.positive_delta_total}</Table.Td>
                    <Table.Td>{adjustment.negative_delta_total}</Table.Td>
                    <Table.Td>{formatCurrency(adjustment.total_cost_impact)}</Table.Td>
                    <Table.Td>
                      <Group justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(adjustment)}>
                          <IconEye size={16} />
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
        <Text c="dimmed">Документы инвентаризации не найдены.</Text>
      )}
    </SectionCard>
  );
}
