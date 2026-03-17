import { ActionIcon, Badge, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { OperationCatalog } from "@/entities/operations/model/types";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type OperationsTableProps = {
  items: OperationCatalog[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (operation: OperationCatalog) => void;
};

export function OperationsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onEdit
}: OperationsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1080}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Операция</Table.Th>
                  <Table.Th>Группа</Table.Th>
                  <Table.Th>Норма</Table.Th>
                  <Table.Th>Тарифы</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((operation) => (
                  <Table.Tr key={operation.id}>
                    <Table.Td>
                      <Text fw={700}>{operation.name}</Text>
                      <Text c="dimmed" size="sm">
                        {operation.code}
                        {operation.description ? ` · ${operation.description}` : ""}
                      </Text>
                    </Table.Td>
                    <Table.Td>{operation.operation_group ?? "—"}</Table.Td>
                    <Table.Td>
                      <Text size="sm">Кол-во: {operation.default_quantity}</Text>
                      <Text c="dimmed" size="sm">
                        Часы: {operation.default_duration_hours}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        {operation.rates.length ? (
                          operation.rates.slice(0, 2).map((rate) => (
                            <Badge key={rate.id} radius="xl" variant="light">
                              {rate.executor_category_code}: {rate.labor_rate}
                            </Badge>
                          ))
                        ) : (
                          <Text c="dimmed" size="sm">
                            Нет ставок
                          </Text>
                        )}
                        {operation.rates.length > 2 ? (
                          <Badge color="gray" radius="xl" variant="light">
                            +{operation.rates.length - 2}
                          </Badge>
                        ) : null}
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <StatusPill kind="boolean" value={operation.is_active} />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(operation)}>
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
        <Text c="dimmed">Операции не найдены.</Text>
      )}
    </SectionCard>
  );
}
