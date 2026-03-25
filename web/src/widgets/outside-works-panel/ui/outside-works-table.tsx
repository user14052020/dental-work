import { ActionIcon, Badge, Group, Loader, Table, Text } from "@mantine/core";
import { IconArrowBackUp, IconExternalLink, IconEye } from "@tabler/icons-react";

import { OutsideWorkItem } from "@/entities/narads/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type OutsideWorksTableProps = {
  items: OutsideWorkItem[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (naradId: string) => void;
  onMarkSent: (item: OutsideWorkItem) => void;
  onMarkReturned: (item: OutsideWorkItem) => void;
};

function outsideStatusLabel(item: OutsideWorkItem) {
  if (item.outside_status === "returned") {
    return "Возвращен";
  }
  if (item.outside_status === "overdue") {
    return "Просрочен";
  }
  return "На стороне";
}

function outsideStatusColor(item: OutsideWorkItem) {
  if (item.outside_status === "returned") {
    return "teal";
  }
  if (item.outside_status === "overdue") {
    return "red";
  }
  return "orange";
}

export function OutsideWorksTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView,
  onMarkSent,
  onMarkReturned
}: OutsideWorksTableProps) {
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
                  <Table.Th>Наряд</Table.Th>
                  <Table.Th>Клиент</Table.Th>
                  <Table.Th>Подрядчик</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th>Отправлено</Table.Th>
                  <Table.Th>Вернуть до</Table.Th>
                  <Table.Th>Стоимость</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((item) => (
                  <Table.Tr key={item.narad_id}>
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
                        {item.doctor_name ?? "Врач не указан"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text fw={600}>{item.contractor_name ?? item.outside_lab_name ?? "—"}</Text>
                      <Text c="dimmed" size="sm">
                        {item.outside_order_number ?? "Без внешнего номера"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" wrap="wrap">
                        <Badge color={outsideStatusColor(item)} radius="xl" variant="light">
                          {outsideStatusLabel(item)}
                        </Badge>
                        <StatusPill value={item.status} />
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm">{formatDateTime(item.outside_sent_at)}</Text>
                      {item.outside_returned_at ? (
                        <Text c="dimmed" size="sm">
                          Возврат: {formatDateTime(item.outside_returned_at)}
                        </Text>
                      ) : null}
                    </Table.Td>
                    <Table.Td>{formatDateTime(item.outside_due_at)}</Table.Td>
                    <Table.Td>{formatCurrency(item.outside_cost)}</Table.Td>
                    <Table.Td>
                      <Group justify="flex-end" gap="xs">
                        <ActionIcon variant="light" onClick={() => onView(item.narad_id)}>
                          <IconEye size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" color="orange" onClick={() => onMarkSent(item)}>
                          <IconExternalLink size={16} />
                        </ActionIcon>
                        <ActionIcon
                          variant="light"
                          color="teal"
                          disabled={item.outside_status === "returned"}
                          onClick={() => onMarkReturned(item)}
                        >
                          <IconArrowBackUp size={16} />
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
        <Text c="dimmed">Наряды на стороне не найдены.</Text>
      )}
    </SectionCard>
  );
}
