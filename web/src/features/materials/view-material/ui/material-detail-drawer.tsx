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
              { label: "В резерве", value: detailQuery.data.reserved_stock },
              { label: "Доступно", value: detailQuery.data.available_stock },
              { label: "Складская стоимость", value: formatCurrency(detailQuery.data.stock_value) },
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

          <div>
            <Text fw={700} mb="sm">
              Последние движения
            </Text>
            <Stack gap="sm">
              {detailQuery.data.movements.length ? (
                detailQuery.data.movements.map((movement) => (
                  <div key={movement.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                    <Group justify="space-between" align="start" wrap="wrap">
                      <div>
                        <Text fw={600}>{movement.movement_type}</Text>
                        <Text c="dimmed" size="sm">
                          {formatDateTime(movement.created_at)}
                        </Text>
                      </div>
                      <Text fw={700}>{movement.quantity_delta}</Text>
                    </Group>
                    <Text c="dimmed" size="sm">
                      Сумма: {formatCurrency(movement.total_cost)} · Остаток после: {movement.balance_after}
                    </Text>
                    {movement.receipt_number ? (
                      <Text c="dimmed" size="sm">
                        Приход: {movement.receipt_number}
                      </Text>
                    ) : null}
                    {movement.work_order_number ? (
                      <Text c="dimmed" size="sm">
                        Заказ: {movement.work_order_number}
                      </Text>
                    ) : null}
                    {movement.inventory_adjustment_number ? (
                      <Text c="dimmed" size="sm">
                        Инвентаризация: {movement.inventory_adjustment_number}
                      </Text>
                    ) : null}
                    {movement.comment ? (
                      <Text c="dimmed" size="sm">
                        {movement.comment}
                      </Text>
                    ) : null}
                  </div>
                ))
              ) : (
                <Text c="dimmed">История движений пока пуста.</Text>
              )}
            </Stack>
          </div>
        </Stack>
      )}
    </Drawer>
  );
}
