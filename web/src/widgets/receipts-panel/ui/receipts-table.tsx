import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEye } from "@tabler/icons-react";

import { MaterialReceiptCompact } from "@/entities/receipts/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";

type ReceiptsTableProps = {
  items: MaterialReceiptCompact[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (receipt: MaterialReceiptCompact) => void;
};

export function ReceiptsTable({ items, meta, isLoading, onPageChange, onView }: ReceiptsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={960}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Приход</Table.Th>
                  <Table.Th>Поставщик</Table.Th>
                  <Table.Th>Позиций</Table.Th>
                  <Table.Th>Количество</Table.Th>
                  <Table.Th>Сумма</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((receipt) => (
                  <Table.Tr key={receipt.id}>
                    <Table.Td>
                      <Text fw={700}>{receipt.receipt_number}</Text>
                      <Text c="dimmed" size="sm">
                        {formatDateTime(receipt.received_at)}
                      </Text>
                    </Table.Td>
                    <Table.Td>{receipt.supplier ?? "—"}</Table.Td>
                    <Table.Td>{receipt.items_count}</Table.Td>
                    <Table.Td>{receipt.total_quantity}</Table.Td>
                    <Table.Td>{formatCurrency(receipt.total_amount)}</Table.Td>
                    <Table.Td>
                      <Group justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(receipt)}>
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
        <Text c="dimmed">Приходы не найдены.</Text>
      )}
    </SectionCard>
  );
}
