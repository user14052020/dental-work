import { ActionIcon, Badge, Checkbox, Group, Loader, Table, Text, Tooltip } from "@mantine/core";
import { IconEye, IconPencil } from "@tabler/icons-react";

import { DeliveryItem } from "@/entities/delivery/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type DeliveryTableProps = {
  items: DeliveryItem[];
  meta?: PageMeta;
  isLoading: boolean;
  selectedIds: string[];
  onToggleSelected: (naradId: string) => void;
  onToggleAll: (naradIds: string[]) => void;
  onPageChange: (page: number) => void;
  onView: (naradId: string) => void;
  canEditDelivery: boolean;
  onEditDelivery: (item: DeliveryItem) => void;
};

export function DeliveryTable({
  items,
  meta,
  isLoading,
  selectedIds,
  onToggleSelected,
  onToggleAll,
  onPageChange,
  onView,
  canEditDelivery,
  onEditDelivery
}: DeliveryTableProps) {
  const visibleIds = items.map((item) => item.id);
  const allSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));
  const someSelected = visibleIds.some((id) => selectedIds.includes(id));

  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1280}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th w={44}>
                    <Checkbox
                      checked={allSelected}
                      indeterminate={!allSelected && someSelected}
                      onChange={() => onToggleAll(visibleIds)}
                    />
                  </Table.Th>
                  <Table.Th>Наряд</Table.Th>
                  <Table.Th>Клиент</Table.Th>
                  <Table.Th>Адрес доставки</Table.Th>
                  <Table.Th>Контакт</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th>Отправка</Table.Th>
                  <Table.Th>Сумма</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((item) => (
                  <Table.Tr key={item.id}>
                    <Table.Td>
                      <Checkbox
                        checked={selectedIds.includes(item.id)}
                        onChange={() => onToggleSelected(item.id)}
                      />
                    </Table.Td>
                    <Table.Td>
                      <Text fw={700}>{item.narad_number}</Text>
                      <Text c="dimmed" size="sm">
                        {item.title}
                        {item.patient_name ? ` · ${item.patient_name}` : ""}
                      </Text>
                      <Text c="dimmed" size="sm">
                        {item.work_numbers.join(", ") || "—"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text fw={600}>{item.client_name}</Text>
                      <Text c="dimmed" size="sm">
                        {item.executor_names.length ? item.executor_names.join(", ") : "Исполнитель не назначен"}
                      </Text>
                      <Text c="dimmed" size="sm">
                        {item.work_types.length ? item.work_types.join(", ") : "Типы работ не указаны"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group justify="space-between" align="start" wrap="nowrap" gap="xs">
                        <Text size="sm">{item.delivery_address ?? "—"}</Text>
                        {canEditDelivery ? (
                          <Tooltip label="Редактировать доставку">
                            <ActionIcon variant="subtle" color="gray" onClick={() => onEditDelivery(item)}>
                              <IconPencil size={16} />
                            </ActionIcon>
                          </Tooltip>
                        ) : null}
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm">{item.delivery_contact ?? "—"}</Text>
                      <Text c="dimmed" size="sm">
                        {item.delivery_phone ?? "—"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" wrap="wrap">
                        <StatusPill value={item.status} />
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Badge color={item.delivery_sent ? "teal" : "gray"} radius="xl" variant="light">
                        {item.delivery_sent ? formatDateTime(item.delivery_sent_at) : "Не отправлено"}
                      </Badge>
                    </Table.Td>
                    <Table.Td>{formatCurrency(item.total_price)}</Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(item.id)}>
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
        <Text c="dimmed">Наряды для доставки не найдены.</Text>
      )}
    </SectionCard>
  );
}
