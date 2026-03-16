"use client";

import { Button, Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { useMaterialDetailQuery } from "@/entities/materials/model/use-materials-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";

type MaterialDetailDrawerProps = {
  materialId?: string;
  opened: boolean;
  onClose: () => void;
  onEdit: () => void;
  onConsume: () => void;
};

export function MaterialDetailDrawer({
  materialId,
  opened,
  onClose,
  onEdit,
  onConsume
}: MaterialDetailDrawerProps) {
  const detailQuery = useMaterialDetailQuery(materialId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Карточка материала">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <Group justify="space-between">
            <div>
              <Text fw={800} size="xl">
                {detailQuery.data.name}
              </Text>
              <Text c="dimmed">{detailQuery.data.category ?? "Категория не указана"}</Text>
            </div>
            <Text fw={700}>{formatMaterialUnit(detailQuery.data.unit)}</Text>
          </Group>

          <DetailGrid
            items={[
              { label: "Остаток", value: detailQuery.data.stock },
              { label: "Минимальный остаток", value: detailQuery.data.min_stock },
              { label: "Цена закупки", value: formatCurrency(detailQuery.data.purchase_price) },
              { label: "Средняя цена", value: formatCurrency(detailQuery.data.average_price) },
              { label: "Поставщик", value: detailQuery.data.supplier ?? "—" },
              { label: "Создан", value: formatDateTime(detailQuery.data.created_at) },
              { label: "Обновлен", value: formatDateTime(detailQuery.data.updated_at) },
              { label: "Комментарий", value: detailQuery.data.comment ?? "—" }
            ]}
          />

          <Group justify="flex-end">
            <Button variant="light" onClick={onConsume}>
              Списать
            </Button>
            <Button variant="light" onClick={onEdit}>
              Редактировать
            </Button>
          </Group>
        </Stack>
      )}
    </Drawer>
  );
}
