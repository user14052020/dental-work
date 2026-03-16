import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit, IconEye } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { PageMeta } from "@/shared/types/api";

type ClientsTableProps = {
  items: Client[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (client: Client) => void;
  onEdit: (client: Client) => void;
};

export function ClientsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView,
  onEdit
}: ClientsTableProps) {
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
                  <Table.Th>Клиент</Table.Th>
                  <Table.Th>Контакт</Table.Th>
                  <Table.Th>Заказов</Table.Th>
                  <Table.Th>Сумма</Table.Th>
                  <Table.Th>Неоплачено</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((client) => (
                  <Table.Tr key={client.id}>
                    <Table.Td>
                      <Text fw={700}>{client.name}</Text>
                      <Text c="dimmed" size="sm">
                        {client.address ?? "Адрес не указан"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text>{client.contact_person ?? "—"}</Text>
                      <Text c="dimmed" size="sm">
                        {client.email ?? client.phone ?? "Нет реквизитов"}
                      </Text>
                    </Table.Td>
                    <Table.Td>{client.work_count}</Table.Td>
                    <Table.Td>{formatCurrency(client.order_total)}</Table.Td>
                    <Table.Td>{formatCurrency(client.unpaid_total)}</Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(client)}>
                          <IconEye size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" onClick={() => onEdit(client)}>
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
        <Text c="dimmed">Клиенты не найдены. Уточните поисковый запрос или создайте новую карточку.</Text>
      )}
    </SectionCard>
  );
}
