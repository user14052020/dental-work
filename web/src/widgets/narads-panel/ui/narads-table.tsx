import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEye } from "@tabler/icons-react";

import { NaradCompact } from "@/entities/narads/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type NaradsTableProps = {
  items: NaradCompact[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (narad: NaradCompact) => void;
};

export function NaradsTable({ items, meta, isLoading, onPageChange, onView }: NaradsTableProps) {
  return (
    <SectionCard className="min-w-0 overflow-hidden">
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={980} type="native">
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Наряд</Table.Th>
                  <Table.Th>Клиент</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th>Работ</Table.Th>
                  <Table.Th>Дедлайн</Table.Th>
                  <Table.Th>Сумма</Table.Th>
                  <Table.Th>Оплачено</Table.Th>
                  <Table.Th>Остаток</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((narad) => (
                  <Table.Tr key={narad.id}>
                    <Table.Td>
                      <Text fw={700}>{narad.narad_number}</Text>
                      <Text c="dimmed" size="sm">
                        {narad.title}
                      </Text>
                      <Text c="dimmed" size="sm">
                        {narad.patient_name ?? narad.doctor_name ?? formatDateTime(narad.received_at)}
                      </Text>
                    </Table.Td>
                    <Table.Td>{narad.client_name}</Table.Td>
                    <Table.Td>
                      <StatusPill value={narad.status} />
                    </Table.Td>
                    <Table.Td>{narad.works_count}</Table.Td>
                    <Table.Td>{formatDateTime(narad.deadline_at)}</Table.Td>
                    <Table.Td>{formatCurrency(narad.total_price)}</Table.Td>
                    <Table.Td>{formatCurrency(narad.amount_paid)}</Table.Td>
                    <Table.Td>{formatCurrency(narad.balance_due)}</Table.Td>
                    <Table.Td>
                      <Group justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(narad)}>
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
        <Text c="dimmed">Наряды не найдены.</Text>
      )}
    </SectionCard>
  );
}
