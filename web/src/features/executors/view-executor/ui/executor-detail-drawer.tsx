"use client";

import { Button, Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { useExecutorDetailQuery } from "@/entities/executors/model/use-executors-query";
import { ArchiveExecutorButton } from "@/features/executors/archive-executor/ui/archive-executor-button";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";
import { StatusPill } from "@/shared/ui/status-pill";

type ExecutorDetailDrawerProps = {
  executorId?: string;
  opened: boolean;
  onClose: () => void;
  onEdit: () => void;
};

export function ExecutorDetailDrawer({
  executorId,
  opened,
  onClose,
  onEdit
}: ExecutorDetailDrawerProps) {
  const detailQuery = useExecutorDetailQuery(executorId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Карточка исполнителя">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <Group justify="space-between">
            <div>
              <Text fw={800} size="xl">
                {detailQuery.data.full_name}
              </Text>
              <Text c="dimmed">{detailQuery.data.specialization ?? "Специализация не указана"}</Text>
            </div>
            <StatusPill kind="boolean" value={detailQuery.data.is_active} />
          </Group>

          <DetailGrid
            items={[
              { label: "Телефон", value: detailQuery.data.phone ?? "—" },
              { label: "Эл. почта", value: detailQuery.data.email ?? "—" },
              { label: "Ставка / час", value: formatCurrency(detailQuery.data.hourly_rate) },
              { label: "Работ", value: String(detailQuery.data.work_count) },
              { label: "Производство", value: formatCurrency(detailQuery.data.production_total) },
              { label: "Создан", value: formatDateTime(detailQuery.data.created_at) },
              { label: "Обновлен", value: formatDateTime(detailQuery.data.updated_at) },
              { label: "Комментарий", value: detailQuery.data.comment ?? "—" }
            ]}
          />

          <Group justify="flex-end">
            <ArchiveExecutorButton executorId={detailQuery.data.id} onArchived={onClose} />
            <Button variant="light" onClick={onEdit}>
              Редактировать
            </Button>
          </Group>
        </Stack>
      )}
    </Drawer>
  );
}
