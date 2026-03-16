"use client";

import { Button, Divider, Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { useWorkDetailQuery } from "@/entities/works/model/use-works-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";
import { StatusPill } from "@/shared/ui/status-pill";

type WorkDetailDrawerProps = {
  workId?: string;
  opened: boolean;
  onClose: () => void;
  onStatusChange: () => void;
};

export function WorkDetailDrawer({
  workId,
  opened,
  onClose,
  onStatusChange
}: WorkDetailDrawerProps) {
  const detailQuery = useWorkDetailQuery(workId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="xl" title="Карточка работы">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <Group justify="space-between" align="start">
            <div>
              <Text fw={800} size="xl">
                {detailQuery.data.order_number}
              </Text>
              <Text c="dimmed">
                {detailQuery.data.client_name} · {detailQuery.data.work_type}
              </Text>
            </div>
            <StatusPill value={detailQuery.data.status} />
          </Group>

          <DetailGrid
            items={[
              { label: "Клиент", value: detailQuery.data.client_name },
              { label: "Исполнитель", value: detailQuery.data.executor_name ?? "—" },
              { label: "Принята", value: formatDateTime(detailQuery.data.received_at) },
              { label: "Дедлайн", value: formatDateTime(detailQuery.data.deadline_at) },
              { label: "Завершена", value: formatDateTime(detailQuery.data.completed_at) },
              { label: "Цена клиенту", value: formatCurrency(detailQuery.data.price_for_client) },
              { label: "Себестоимость", value: formatCurrency(detailQuery.data.cost_price) },
              { label: "Маржа", value: formatCurrency(detailQuery.data.margin) },
              { label: "Оплачено", value: formatCurrency(detailQuery.data.amount_paid) },
              { label: "Доп. расходы", value: formatCurrency(detailQuery.data.additional_expenses) },
              { label: "Трудозатраты", value: detailQuery.data.labor_hours },
              { label: "Комментарий", value: detailQuery.data.comment ?? "—" }
            ]}
          />

          {detailQuery.data.description ? (
            <>
              <Divider />
              <div>
                <Text c="dimmed" size="sm">
                  Описание
                </Text>
                <Text mt={6}>{detailQuery.data.description}</Text>
              </div>
            </>
          ) : null}

          <Divider />
          <Stack gap="sm">
            <Text fw={700}>Материалы</Text>
            {detailQuery.data.materials.length ? (
              detailQuery.data.materials.map((line) => (
                <div key={line.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>{line.material_name}</Text>
                  <Text c="dimmed" size="sm">
                    {line.quantity} × {formatCurrency(line.unit_cost)} = {formatCurrency(line.total_cost)}
                  </Text>
                </div>
              ))
            ) : (
              <Text c="dimmed">Материалы пока не привязаны.</Text>
            )}
          </Stack>

          <Group justify="flex-end">
            <Button variant="light" onClick={onStatusChange}>
              Изменить статус
            </Button>
          </Group>
        </Stack>
      )}
    </Drawer>
  );
}
