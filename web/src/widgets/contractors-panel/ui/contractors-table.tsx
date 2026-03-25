import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { Contractor } from "@/entities/contractors/model/types";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type ContractorsTableProps = {
  items: Contractor[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (contractor: Contractor) => void;
};

export function ContractorsTable({ items, meta, isLoading, onPageChange, onEdit }: ContractorsTableProps) {
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
                  <Table.Th>Подрядчик</Table.Th>
                  <Table.Th>Контакт</Table.Th>
                  <Table.Th>Адрес</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((contractor) => (
                  <Table.Tr key={contractor.id}>
                    <Table.Td>
                      <Text fw={700}>{contractor.name}</Text>
                      <Text c="dimmed" size="sm">
                        {contractor.comment ?? "Без комментария"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text>{contractor.contact_person ?? "—"}</Text>
                      <Text c="dimmed" size="sm">
                        {contractor.phone ?? contractor.email ?? "Нет контактных данных"}
                      </Text>
                    </Table.Td>
                    <Table.Td>{contractor.address ?? "—"}</Table.Td>
                    <Table.Td>
                      <StatusPill kind="boolean" value={contractor.is_active} />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(contractor)}>
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
        <Text c="dimmed">Подрядчики не найдены.</Text>
      )}
    </SectionCard>
  );
}
