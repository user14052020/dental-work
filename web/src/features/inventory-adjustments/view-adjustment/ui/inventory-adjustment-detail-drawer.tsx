"use client";

import { Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { useInventoryAdjustmentDetailQuery } from "@/entities/inventory-adjustments/model/use-inventory-adjustments-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";

type InventoryAdjustmentDetailDrawerProps = {
  adjustmentId?: string;
  opened: boolean;
  onClose: () => void;
};

export function InventoryAdjustmentDetailDrawer({
  adjustmentId,
  opened,
  onClose
}: InventoryAdjustmentDetailDrawerProps) {
  const detailQuery = useInventoryAdjustmentDetailQuery(adjustmentId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Карточка инвентаризации">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <DetailGrid
            items={[
              { label: "Номер", value: detailQuery.data.adjustment_number },
              { label: "Дата", value: formatDateTime(detailQuery.data.recorded_at) },
              { label: "Позиций", value: String(detailQuery.data.items_count) },
              { label: "Изменено", value: String(detailQuery.data.changed_items_count) },
              { label: "Прибавка", value: detailQuery.data.positive_delta_total },
              { label: "Списание", value: detailQuery.data.negative_delta_total },
              { label: "Влияние на стоимость", value: formatCurrency(detailQuery.data.total_cost_impact) },
              { label: "Комментарий", value: detailQuery.data.comment ?? "—" }
            ]}
          />

          <div>
            <Text fw={700} mb="sm">
              Строки инвентаризации
            </Text>
            <Stack gap="sm">
              {detailQuery.data.items.map((item) => (
                <div key={item.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>{item.material_name}</Text>
                  <Text c="dimmed" size="sm">
                    Ожидалось: {item.expected_stock} · Фактически: {item.actual_stock} · Отклонение: {item.quantity_delta}
                  </Text>
                  <Text c="dimmed" size="sm">
                    Себестоимость: {formatCurrency(item.total_cost)}
                  </Text>
                  {item.comment ? (
                    <Text c="dimmed" size="sm">
                      {item.comment}
                    </Text>
                  ) : null}
                </div>
              ))}
            </Stack>
          </div>
        </Stack>
      )}
    </Drawer>
  );
}
