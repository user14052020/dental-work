import { ActionIcon, Badge, Group, Loader, Table, Text } from "@mantine/core";
import { IconEdit, IconEye, IconMinus } from "@tabler/icons-react";

import { Material } from "@/entities/materials/model/types";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { PageMeta } from "@/shared/types/api";
import { PaginationControls } from "@/shared/ui/pagination-controls";
import { SectionCard } from "@/shared/ui/section-card";

type MaterialsTableProps = {
  items: Material[];
  meta?: PageMeta;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onView: (material: Material) => void;
  onEdit: (material: Material) => void;
  onConsume: (material: Material) => void;
};

export function MaterialsTable({
  items,
  meta,
  isLoading,
  onPageChange,
  onView,
  onEdit,
  onConsume
}: MaterialsTableProps) {
  return (
    <SectionCard>
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : items.length ? (
        <>
          <Table.ScrollContainer minWidth={960}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Материал</Table.Th>
                  <Table.Th>Остаток</Table.Th>
                  <Table.Th>Средняя цена</Table.Th>
                  <Table.Th>Поставщик</Table.Th>
                  <Table.Th>Статус</Table.Th>
                  <Table.Th />
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((material) => (
                  <Table.Tr key={material.id}>
                    <Table.Td>
                      <Text fw={700}>{material.name}</Text>
                      <Text c="dimmed" size="sm">
                        {material.category ?? "Без категории"} · {formatMaterialUnit(material.unit)}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      {material.stock} / мин. {material.min_stock}
                    </Table.Td>
                    <Table.Td>{formatCurrency(material.average_price)}</Table.Td>
                    <Table.Td>{material.supplier ?? "—"}</Table.Td>
                    <Table.Td>
                      <Badge color={material.is_low_stock ? "red" : "teal"} radius="xl" variant="light">
                        {material.is_low_stock ? "Низкий остаток" : "Норма"}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon variant="light" onClick={() => onView(material)}>
                          <IconEye size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" onClick={() => onEdit(material)}>
                          <IconEdit size={16} />
                        </ActionIcon>
                        <ActionIcon variant="light" onClick={() => onConsume(material)}>
                          <IconMinus size={16} />
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
        <Text c="dimmed">Материалы не найдены.</Text>
      )}
    </SectionCard>
  );
}
