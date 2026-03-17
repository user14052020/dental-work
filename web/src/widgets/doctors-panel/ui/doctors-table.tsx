import { ActionIcon, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit } from "@tabler/icons-react";

import { Doctor } from "@/entities/doctors/model/types";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

type DoctorsTableProps = {
  items: Doctor[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (doctor: Doctor) => void;
};

export function DoctorsTable({ items, meta, isLoading, onPageChange, onEdit }: DoctorsTableProps) {
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
                  <Table.Th>Врач</Table.Th>
                  <Table.Th>Клиника</Table.Th>
                  <Table.Th>Контакты</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((doctor) => (
                  <Table.Tr key={doctor.id}>
                    <Table.Td>
                      <Text fw={700}>{doctor.full_name}</Text>
                      <Text c="dimmed" size="sm">
                        {doctor.specialization ?? "Специализация не указана"}
                      </Text>
                    </Table.Td>
                    <Table.Td>{doctor.client_name ?? "Не привязан"}</Table.Td>
                    <Table.Td>
                      <Text>{doctor.phone ?? "—"}</Text>
                      <Text c="dimmed" size="sm">
                        {doctor.email ?? doctor.comment ?? "Нет дополнительных данных"}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <StatusPill kind="boolean" value={doctor.is_active} />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onEdit(doctor)}>
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
        <Text c="dimmed">Врачи не найдены.</Text>
      )}
    </SectionCard>
  );
}
