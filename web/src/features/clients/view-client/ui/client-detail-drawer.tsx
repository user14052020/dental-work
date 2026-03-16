"use client";

import { Button, Divider, Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { useClientDetailQuery } from "@/entities/clients/model/use-clients-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";

import { DeleteClientButton } from "@/features/clients/delete-client/ui/delete-client-button";

type ClientDetailDrawerProps = {
  clientId?: string;
  opened: boolean;
  onClose: () => void;
  onEdit: () => void;
};

export function ClientDetailDrawer({ clientId, opened, onClose, onEdit }: ClientDetailDrawerProps) {
  const detailQuery = useClientDetailQuery(clientId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Карточка клиента">
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
              <Text c="dimmed">{detailQuery.data.contact_person ?? "Контактное лицо не указано"}</Text>
            </div>
            <Group>
              <DeleteClientButton clientId={detailQuery.data.id} onDeleted={onClose} />
              <Button variant="light" onClick={onEdit}>
                Редактировать
              </Button>
            </Group>
          </Group>

          <DetailGrid
            items={[
              { label: "Телефон", value: detailQuery.data.phone ?? "—" },
              { label: "Эл. почта", value: detailQuery.data.email ?? "—" },
              { label: "Адрес", value: detailQuery.data.address ?? "—" },
              { label: "Заказов", value: String(detailQuery.data.work_count) },
              { label: "Сумма заказов", value: formatCurrency(detailQuery.data.order_total) },
              { label: "Неоплачено", value: formatCurrency(detailQuery.data.unpaid_total) },
              { label: "Создан", value: formatDateTime(detailQuery.data.created_at) },
              { label: "Обновлен", value: formatDateTime(detailQuery.data.updated_at) }
            ]}
          />

          {detailQuery.data.comment ? (
            <>
              <Divider />
              <div>
                <Text c="dimmed" size="sm">
                  Комментарий
                </Text>
                <Text mt={6}>{detailQuery.data.comment}</Text>
              </div>
            </>
          ) : null}

          <Divider />
          <Stack gap="sm">
            <Text fw={700}>Последние работы</Text>
            {detailQuery.data.recent_works.length ? (
              detailQuery.data.recent_works.map((work) => (
                <div key={work.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>
                    {work.order_number} · {work.work_type}
                  </Text>
                  <Text c="dimmed" size="sm">
                    {formatCurrency(work.price_for_client)} · {formatDateTime(work.received_at)}
                  </Text>
                </div>
              ))
            ) : (
              <Text c="dimmed">История работ пока пуста.</Text>
            )}
          </Stack>
        </Stack>
      )}
    </Drawer>
  );
}
