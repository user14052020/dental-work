import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit, IconTrash } from "@tabler/icons-react";

import { PaymentCompact, paymentMethodOptions } from "@/entities/payments/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { PageMeta } from "@/shared/types/api";

type PaymentsTableProps = {
  items: PaymentCompact[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (payment: PaymentCompact) => void;
  onDelete: (payment: PaymentCompact) => void;
};

const paymentMethodLabels = Object.fromEntries(
  paymentMethodOptions.map((option) => [option.value, option.label])
) as Record<string, string>;

export function PaymentsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onEdit,
  onDelete
}: PaymentsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={980}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Платеж</Table.Th>
                  <Table.Th>Клиент</Table.Th>
                  <Table.Th>Дата</Table.Th>
                  <Table.Th>Способ</Table.Th>
                  <Table.Th>Сумма</Table.Th>
                  <Table.Th>Распределено</Table.Th>
                  <Table.Th>Остаток</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((payment) => (
                  <Table.Tr key={payment.id}>
                    <Table.Td>
                      <Text fw={700}>{payment.payment_number}</Text>
                      <Text c="dimmed" size="sm">
                        {payment.external_reference || payment.comment || "Без дополнительной ссылки"}
                      </Text>
                    </Table.Td>
                    <Table.Td>{payment.client_name}</Table.Td>
                    <Table.Td>{formatDateTime(payment.payment_date)}</Table.Td>
                    <Table.Td>{paymentMethodLabels[payment.method] ?? payment.method}</Table.Td>
                    <Table.Td>{formatCurrency(payment.amount)}</Table.Td>
                    <Table.Td>{formatCurrency(payment.allocated_total)}</Table.Td>
                    <Table.Td>{formatCurrency(payment.unallocated_total)}</Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(payment)}>
                          <IconEdit size={16} />
                        </ActionIcon>
                        <ActionIcon color="red" variant="light" onClick={() => onDelete(payment)}>
                          <IconTrash size={16} />
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
        <Text c="dimmed">Платежи пока не созданы.</Text>
      )}
    </SectionCard>
  );
}
