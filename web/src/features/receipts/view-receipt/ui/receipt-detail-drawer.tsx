"use client";

import { Drawer, Group, Loader, Stack, Text } from "@mantine/core";

import { useReceiptDetailQuery } from "@/entities/receipts/model/use-receipts-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";

type ReceiptDetailDrawerProps = {
  receiptId?: string;
  opened: boolean;
  onClose: () => void;
};

export function ReceiptDetailDrawer({ receiptId, opened, onClose }: ReceiptDetailDrawerProps) {
  const detailQuery = useReceiptDetailQuery(receiptId);

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Карточка прихода">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <DetailGrid
            items={[
              { label: "Номер", value: detailQuery.data.receipt_number },
              { label: "Дата", value: formatDateTime(detailQuery.data.received_at) },
              { label: "Поставщик", value: detailQuery.data.supplier ?? "—" },
              { label: "Позиций", value: String(detailQuery.data.items_count) },
              { label: "Количество", value: detailQuery.data.total_quantity },
              { label: "Сумма", value: formatCurrency(detailQuery.data.total_amount) },
              { label: "Комментарий", value: detailQuery.data.comment ?? "—" }
            ]}
          />

          <div>
            <Text fw={700} mb="sm">
              Строки прихода
            </Text>
            <Stack gap="sm">
              {detailQuery.data.items.map((item) => (
                <div key={item.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>{item.material_name}</Text>
                  <Text c="dimmed" size="sm">
                    {item.quantity} × {formatCurrency(item.unit_price)} = {formatCurrency(item.total_price)}
                  </Text>
                </div>
              ))}
            </Stack>
          </div>
        </Stack>
      )}
    </Drawer>
  );
}
