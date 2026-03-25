import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconArrowAutofitRight, IconEye } from "@tabler/icons-react";

import { WorkCompact } from "@/entities/works/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type WorksTableProps = {
  items: WorkCompact[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (work: WorkCompact) => void;
  onStatusChange: (work: WorkCompact) => void;
};

export function WorksTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView,
  onStatusChange
}: WorksTableProps) {
  return (
    <SectionCard className="min-w-0 overflow-hidden">
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1040} type="native">
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Заказ</Table.Th>
                  <Table.Th>Тип работы</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th>Дедлайн</Table.Th>
                  <Table.Th>Цена</Table.Th>
                  <Table.Th>Себестоимость</Table.Th>
                  <Table.Th>Маржа</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((work) => (
                  <Table.Tr key={work.id}>
                    <Table.Td>
                      <Text fw={700}>{work.order_number}</Text>
                      <Text c="dimmed" size="sm">
                        Наряд {work.narad_number}
                      </Text>
                    </Table.Td>
                    <Table.Td>{work.work_type}</Table.Td>
                    <Table.Td>
                      <StatusPill value={work.status} />
                    </Table.Td>
                    <Table.Td>{formatDateTime(work.deadline_at)}</Table.Td>
                    <Table.Td>{formatCurrency(work.price_for_client)}</Table.Td>
                    <Table.Td>{formatCurrency(work.cost_price)}</Table.Td>
                    <Table.Td>{formatCurrency(work.margin)}</Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(work)}>
                          <IconEye size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" onClick={() => onStatusChange(work)}>
                          <IconArrowAutofitRight size={16} />
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
        <Text c="dimmed">Работы не найдены.</Text>
      )}
    </SectionCard>
  );
}
