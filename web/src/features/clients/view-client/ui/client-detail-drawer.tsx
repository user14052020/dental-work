"use client";

import { Button, Divider, Drawer, Group, Loader, Stack, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { useClientDetailQuery } from "@/entities/clients/model/use-clients-query";
import { paymentMethodOptions } from "@/entities/payments/model/types";
import { DeleteClientButton } from "@/features/clients/delete-client/ui/delete-client-button";
import { ClientDocumentsModal } from "@/features/clients/print-client-documents/ui/client-documents-modal";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { DetailGrid } from "@/shared/ui/detail-grid";

type ClientDetailDrawerProps = {
  clientId?: string;
  opened: boolean;
  onClose: () => void;
  onEdit: () => void;
};

function formatDateOnly(value?: string | null) {
  if (!value) {
    return "—";
  }

  return value;
}

export function ClientDetailDrawer({ clientId, opened, onClose, onEdit }: ClientDetailDrawerProps) {
  const detailQuery = useClientDetailQuery(clientId);
  const [documentsOpened, documentsHandlers] = useDisclosure(false);
  const paymentMethodLabels = Object.fromEntries(
    paymentMethodOptions.map((option) => [option.value, option.label])
  ) as Record<string, string>;

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
              <Button variant="default" onClick={documentsHandlers.open}>
                Документы
              </Button>
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
              { label: "Адрес доставки", value: detailQuery.data.delivery_address ?? "—" },
              { label: "Контакт доставки", value: detailQuery.data.delivery_contact ?? "—" },
              { label: "Телефон доставки", value: detailQuery.data.delivery_phone ?? "—" },
              { label: "Юридическое название", value: detailQuery.data.legal_name ?? "—" },
              { label: "Юридический адрес", value: detailQuery.data.legal_address ?? "—" },
              { label: "ИНН", value: detailQuery.data.inn ?? "—" },
              { label: "КПП", value: detailQuery.data.kpp ?? "—" },
              { label: "ОГРН", value: detailQuery.data.ogrn ?? "—" },
              { label: "Банк", value: detailQuery.data.bank_name ?? "—" },
              { label: "БИК", value: detailQuery.data.bik ?? "—" },
              { label: "Расчетный счет", value: detailQuery.data.settlement_account ?? "—" },
              { label: "Корр. счет", value: detailQuery.data.correspondent_account ?? "—" },
              { label: "Номер договора", value: detailQuery.data.contract_number ?? "—" },
              { label: "Дата договора", value: formatDateOnly(detailQuery.data.contract_date) },
              { label: "Подписант", value: detailQuery.data.signer_name ?? "—" },
              { label: "Скидка / надбавка, %", value: detailQuery.data.default_price_adjustment_percent },
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
            <Text fw={700}>Индивидуальные цены по каталогу</Text>
            {detailQuery.data.work_catalog_prices.length ? (
              detailQuery.data.work_catalog_prices.map((item) => (
                <div key={item.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>
                    {item.work_catalog_item_code} · {item.work_catalog_item_name}
                  </Text>
                  <Text c="dimmed" size="sm">
                    {item.work_catalog_item_category ?? "Без категории"} · {formatCurrency(item.price)}
                  </Text>
                  {item.comment ? (
                    <Text c="dimmed" mt={6} size="sm">
                      {item.comment}
                    </Text>
                  ) : null}
                </div>
              ))
            ) : (
              <Text c="dimmed">Индивидуальные цены для клиента пока не заданы.</Text>
            )}
          </Stack>

          <Divider />
          <Stack gap="sm">
            <Text fw={700}>Последние платежи</Text>
            {detailQuery.data.recent_payments.length ? (
              detailQuery.data.recent_payments.map((payment) => (
                <div key={payment.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>
                    {payment.payment_number} · {formatCurrency(payment.amount)}
                  </Text>
                  <Text c="dimmed" size="sm">
                    {paymentMethodLabels[payment.method] ?? payment.method} · {formatDateTime(payment.payment_date)}
                  </Text>
                  <Text c="dimmed" size="sm">
                    Распределено {formatCurrency(payment.allocated_total)} · остаток {formatCurrency(payment.unallocated_total)}
                  </Text>
                </div>
              ))
            ) : (
              <Text c="dimmed">Платежи по клиенту пока не зарегистрированы.</Text>
            )}
          </Stack>

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
      {detailQuery.data ? (
        <ClientDocumentsModal
          clientId={detailQuery.data.id}
          clientName={detailQuery.data.legal_name ?? detailQuery.data.name}
          clientEmail={detailQuery.data.email}
          opened={documentsOpened}
          onClose={documentsHandlers.close}
        />
      ) : null}
    </Drawer>
  );
}
