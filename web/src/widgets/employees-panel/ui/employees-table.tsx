import { ActionIcon, Badge, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { Employee } from "@/entities/employees/model/types";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type EmployeesTableProps = {
  items: Employee[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (employee: Employee) => void;
};

export function EmployeesTable({ items, meta, isLoading, onPageChange, onEdit }: EmployeesTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={1040}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Сотрудник</Table.Th>
                  <Table.Th>Должность</Table.Th>
                  <Table.Th>Техник</Table.Th>
                  <Table.Th>Доступ</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((employee) => (
                  <Table.Tr key={employee.id}>
                    <Table.Td>
                      <Text fw={700}>{employee.full_name}</Text>
                      <Text c="dimmed" size="sm">
                        {employee.email}
                        {employee.phone ? ` · ${employee.phone}` : ""}
                      </Text>
                    </Table.Td>
                    <Table.Td>{employee.job_title ?? "—"}</Table.Td>
                    <Table.Td>{employee.executor_name ?? "Не привязан"}</Table.Td>
                    <Table.Td>
                      <Badge color={employee.permission_codes.includes("*") ? "teal" : "blue"} radius="xl" variant="light">
                        {employee.permission_codes.includes("*")
                          ? "Полный доступ"
                          : `${employee.permission_codes.length} прав`}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <StatusPill kind="boolean" value={employee.is_active} />
                        {employee.is_fired ? (
                          <Badge color="red" radius="xl" variant="light">
                            Уволен
                          </Badge>
                        ) : null}
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Group justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(employee)}>
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
        <Text c="dimmed">Сотрудники не найдены.</Text>
      )}
    </SectionCard>
  );
}
