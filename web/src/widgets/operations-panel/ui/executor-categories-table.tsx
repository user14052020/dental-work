import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { ExecutorCategory } from "@/entities/operations/model/types";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type ExecutorCategoriesTableProps = {
  isLoading: boolean;
  items: ExecutorCategory[];
  onEdit: (category: ExecutorCategory) => void;
};

export function ExecutorCategoriesTable({
  isLoading,
  items,
  onEdit
}: ExecutorCategoriesTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <Table.ScrollContainer minWidth={840}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Код</Table.Th>
                <Table.Th>Категория</Table.Th>
                <Table.Th>Описание</Table.Th>
                <Table.Th>Порядок</Table.Th>
                <Table.Th>Статус</Table.Th>
                <Table.Th />
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {items.map((category) => (
                <Table.Tr key={category.id}>
                  <Table.Td>
                    <Text fw={700}>{category.code}</Text>
                  </Table.Td>
                  <Table.Td>{category.name}</Table.Td>
                  <Table.Td>
                    <Text c="dimmed" size="sm">
                      {category.description ?? "—"}
                    </Text>
                  </Table.Td>
                  <Table.Td>{category.sort_order}</Table.Td>
                  <Table.Td>
                    <StatusPill kind="boolean" value={category.is_active} />
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" justify="flex-end">
                      <ActionIcon variant="light" onClick={() => onEdit(category)}>
                        <IconEdit size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">Категории оплаты пока не добавлены.</Text>
      )}
    </SectionCard>
  );
}
