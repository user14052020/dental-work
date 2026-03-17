import { ActionIcon, Badge, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { WorkCatalogItem } from "@/entities/work-catalog/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type WorkCatalogTableProps = {
  items: WorkCatalogItem[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (item: WorkCatalogItem) => void;
};

export function WorkCatalogTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onEdit
}: WorkCatalogTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1100}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Работа</Table.Th>
                  <Table.Th>Категория</Table.Th>
                  <Table.Th>База</Table.Th>
                  <Table.Th>Шаблон операций</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((item) => (
                  <Table.Tr key={item.id}>
                    <Table.Td>
                      <Text fw={700}>{item.name}</Text>
                      <Text c="dimmed" size="sm">
                        {item.code}
                        {item.description ? ` · ${item.description}` : ""}
                      </Text>
                    </Table.Td>
                    <Table.Td>{item.category ?? "—"}</Table.Td>
                    <Table.Td>
                      <Text size="sm">{formatCurrency(item.base_price)}</Text>
                      <Text c="dimmed" size="sm">
                        Нормо-часы: {item.default_duration_hours}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        {item.default_operations.length ? (
                          item.default_operations.slice(0, 2).map((operation) => (
                            <Badge key={operation.id} radius="xl" variant="light">
                              {operation.operation_code}: {operation.quantity}
                            </Badge>
                          ))
                        ) : (
                          <Text c="dimmed" size="sm">
                            Нет шаблона
                          </Text>
                        )}
                        {item.default_operations.length > 2 ? (
                          <Badge color="gray" radius="xl" variant="light">
                            +{item.default_operations.length - 2}
                          </Badge>
                        ) : null}
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <StatusPill kind="boolean" value={item.is_active} />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(item)}>
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
        <Text c="dimmed">Каталог работ пока пуст.</Text>
      )}
    </SectionCard>
  );
}
