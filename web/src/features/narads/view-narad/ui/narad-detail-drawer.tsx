"use client";

import { Button, Divider, Drawer, Group, Loader, Stack, Text } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconFileInvoice, IconFileText, IconPrinter } from "@tabler/icons-react";

import { sendNaradDocumentEmail } from "@/entities/documents/api/documents-api";
import { NaradDocumentEmailPayload } from "@/entities/documents/model/types";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { reserveNaradMaterials } from "@/entities/narads/api/narads-api";
import { useNaradDetailQuery } from "@/entities/narads/model/use-narads-query";
import { Narad } from "@/entities/narads/model/types";
import { paymentMethodOptions } from "@/entities/payments/model/types";
import { DocumentEmailModal } from "@/features/documents/send-document-email/ui/document-email-modal";
import { faceShapeOptions, patientGenderOptions } from "@/entities/works/model/types";
import { Odontogram } from "@/entities/works/ui/odontogram";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";
import { DetailGrid } from "@/shared/ui/detail-grid";
import { StatusPill } from "@/shared/ui/status-pill";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { worksQueryKeys } from "@/entities/works/model/query-keys";

const patientGenderLabels = Object.fromEntries(
  patientGenderOptions.map((option) => [option.value, option.label])
) as Record<string, string>;
const faceShapeLabels = Object.fromEntries(faceShapeOptions.map((option) => [option.value, option.label])) as Record<
  string,
  string
>;

function formatOutsideWorkStatus(narad: Narad) {
  if (!narad.is_outside_work) {
    return "Нет";
  }
  if (narad.outside_returned_at) {
    return "Возвращена";
  }
  if (narad.outside_due_at && new Date(narad.outside_due_at).getTime() < Date.now()) {
    return "Просрочена";
  }
  return "На стороне";
}

function openPrintDocument(path: string) {
  if (typeof window === "undefined") {
    return;
  }

  window.open(path, "_blank", "noopener,noreferrer");
}

type NaradDetailDrawerProps = {
  naradId?: string;
  opened: boolean;
  onClose: () => void;
  onAddWork?: (narad: Narad) => void;
  onEdit?: (narad: Narad) => void;
  onCloseNarad?: (narad: Narad) => void;
  onReopenNarad?: (narad: Narad) => void;
};

export function NaradDetailDrawer({
  naradId,
  opened,
  onClose,
  onAddWork,
  onEdit,
  onCloseNarad,
  onReopenNarad
}: NaradDetailDrawerProps) {
  const detailQuery = useNaradDetailQuery(naradId);
  const [emailOpened, emailHandlers] = useDisclosure(false);
  const queryClient = useQueryClient();
  const paymentMethodLabels = new Map<string, string>(paymentMethodOptions.map((item) => [item.value, item.label]));
  const patientGenderLabel = detailQuery.data?.patient_gender
    ? patientGenderLabels[detailQuery.data.patient_gender] ?? detailQuery.data.patient_gender
    : "—";
  const faceShapeLabel = detailQuery.data?.face_shape
    ? faceShapeLabels[detailQuery.data.face_shape] ?? detailQuery.data.face_shape
    : "—";
  const reserveMutation = useMutation({
    mutationFn: () => reserveNaradMaterials(naradId as string),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification("Материалы по наряду зарезервированы.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось зарезервировать материалы.");
    }
  });

  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="xl" title="Карточка наряда">
      {detailQuery.isLoading || !detailQuery.data ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <Stack gap="lg">
          <Group justify="space-between" align="start">
            <div>
              <Text fw={800} size="xl">
                {detailQuery.data.narad_number}
              </Text>
              <Text c="dimmed">
                {detailQuery.data.client_name} · {detailQuery.data.title}
              </Text>
            </div>
            <StatusPill value={detailQuery.data.status} />
          </Group>

          <Group gap="sm" wrap="wrap">
            <Button
              leftSection={<IconFileInvoice size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/narads/${detailQuery.data.id}/invoice`)}
            >
              Счет
            </Button>
            <Button
              leftSection={<IconFileText size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/narads/${detailQuery.data.id}/act`)}
            >
              Акт
            </Button>
            <Button
              leftSection={<IconPrinter size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/narads/${detailQuery.data.id}/job-order`)}
            >
              Наряд
            </Button>
            <Button variant="default" onClick={emailHandlers.open}>
              Отправить по почте
            </Button>
            {!detailQuery.data.is_closed ? (
              <Button
                color="gray"
                loading={reserveMutation.isPending}
                radius="xl"
                variant="light"
                onClick={() => reserveMutation.mutate()}
              >
                Зарезервировать материалы
              </Button>
            ) : null}
            {onEdit ? (
              <Button
                radius="xl"
                variant="light"
                onClick={() => onEdit(detailQuery.data)}
              >
                Редактировать наряд
              </Button>
            ) : null}
            {onAddWork ? (
              <Button
                color="teal"
                radius="xl"
                variant="light"
                onClick={() => onAddWork(detailQuery.data)}
              >
                Добавить работу
              </Button>
            ) : null}
            {detailQuery.data.is_closed ? (
              onReopenNarad ? (
                <Button color="orange" radius="xl" variant="light" onClick={() => onReopenNarad(detailQuery.data)}>
                  Открыть наряд
                </Button>
              ) : null
            ) : onCloseNarad ? (
              <Button color="dark" radius="xl" variant="filled" onClick={() => onCloseNarad(detailQuery.data)}>
                Закрыть наряд
              </Button>
            ) : null}
          </Group>

          <DetailGrid
            items={[
              { label: "Клиент", value: detailQuery.data.client_name },
              { label: "Врач", value: detailQuery.data.doctor_name ?? "—" },
              { label: "Телефон врача", value: detailQuery.data.doctor_phone ?? "—" },
              { label: "Пациент", value: detailQuery.data.patient_name ?? "—" },
              {
                label: "Возраст",
                value:
                  detailQuery.data.patient_age !== null && detailQuery.data.patient_age !== undefined
                    ? String(detailQuery.data.patient_age)
                    : "—"
              },
              { label: "Пол", value: patientGenderLabel },
              { label: "Фото для цвета", value: detailQuery.data.require_color_photo ? "Да" : "Нет" },
              { label: "Форма лица", value: faceShapeLabel },
              { label: "Система имплантов", value: detailQuery.data.implant_system ?? "—" },
              { label: "Металл", value: detailQuery.data.metal_type ?? "—" },
              { label: "Цвет", value: detailQuery.data.shade_color ?? "—" },
              { label: "Зубная формула", value: detailQuery.data.tooth_formula ?? "—" },
              { label: "Принят", value: formatDateTime(detailQuery.data.received_at) },
              { label: "Дедлайн", value: formatDateTime(detailQuery.data.deadline_at) },
              { label: "Завершён", value: formatDateTime(detailQuery.data.completed_at) },
              { label: "Закрыт", value: formatDateTime(detailQuery.data.closed_at) },
              { label: "Работ внутри", value: String(detailQuery.data.works_count) },
              { label: "Сумма", value: formatCurrency(detailQuery.data.total_price) },
              { label: "Себестоимость", value: formatCurrency(detailQuery.data.total_cost) },
              { label: "Маржа", value: formatCurrency(detailQuery.data.total_margin) },
              { label: "Оплачено", value: formatCurrency(detailQuery.data.amount_paid) },
              { label: "Остаток", value: formatCurrency(detailQuery.data.balance_due) }
            ]}
          />

          {detailQuery.data.is_outside_work ? (
            <>
              <Divider />
              <Stack gap="sm">
                <Text fw={700}>Работа на стороне</Text>
                <DetailGrid
                  items={[
                    { label: "Состояние", value: formatOutsideWorkStatus(detailQuery.data) },
                    { label: "Подрядчик", value: detailQuery.data.contractor_name ?? detailQuery.data.outside_lab_name ?? "—" },
                    { label: "Внешний номер", value: detailQuery.data.outside_order_number ?? "—" },
                    { label: "Стоимость", value: formatCurrency(detailQuery.data.outside_cost) },
                    { label: "Отправлено", value: formatDateTime(detailQuery.data.outside_sent_at) },
                    { label: "Вернуть до", value: formatDateTime(detailQuery.data.outside_due_at) },
                    { label: "Возвращено", value: formatDateTime(detailQuery.data.outside_returned_at) }
                  ]}
                />
                {detailQuery.data.outside_comment ? (
                  <div>
                    <Text c="dimmed" size="sm">
                      Комментарий по стороне
                    </Text>
                    <Text mt={6}>{detailQuery.data.outside_comment}</Text>
                  </div>
                ) : null}
              </Stack>
            </>
          ) : null}

          {detailQuery.data.tooth_selection.length ? (
            <>
              <Divider />
              <Stack gap="sm">
                <Text fw={700}>Графическая зубная формула</Text>
                <Odontogram readOnly value={detailQuery.data.tooth_selection} />
              </Stack>
            </>
          ) : null}

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
            <Group justify="space-between" align="center">
              <Text fw={700}>Связанные работы</Text>
              <Text c="dimmed" size="sm">
                {detailQuery.data.works.length} строк(и)
              </Text>
            </Group>
            {detailQuery.data.works.map((work) => (
              <div key={work.id} className="rounded-[20px] bg-slate-50 px-4 py-4">
                <Group justify="space-between" align="start" wrap="wrap">
                  <div>
                    <Text fw={700}>{work.order_number}</Text>
                    <Text c="dimmed" size="sm">
                      {work.work_catalog_item_code ? `${work.work_catalog_item_code} · ` : ""}
                      {work.work_type}
                    </Text>
                  </div>
                  <StatusPill value={work.status} />
                </Group>
                <DetailGrid
                  items={[
                    { label: "Исполнитель", value: work.executor_name ?? "—" },
                    { label: "Принята", value: formatDateTime(work.received_at) },
                    { label: "Дедлайн", value: formatDateTime(work.deadline_at) },
                    { label: "Цена", value: formatCurrency(work.price_for_client) },
                    { label: "Оплачено", value: formatCurrency(work.amount_paid) },
                    { label: "Остаток", value: formatCurrency(work.balance_due) }
                  ]}
                />
              </div>
            ))}
          </Stack>

          <Divider />
          <Stack gap="sm">
            <Group justify="space-between" align="center">
              <Text fw={700}>Платежи по наряду</Text>
              <Text c="dimmed" size="sm">
                {detailQuery.data.payments.length} платеж(а/ей)
              </Text>
            </Group>
            {detailQuery.data.payments.length ? (
              detailQuery.data.payments.map((payment) => (
                <div key={payment.id} className="rounded-[20px] bg-slate-50 px-4 py-4">
                  <Group justify="space-between" align="start" wrap="wrap">
                    <div>
                      <Text fw={700}>{payment.payment_number}</Text>
                      <Text c="dimmed" size="sm">
                        {formatDateTime(payment.payment_date)} · {paymentMethodLabels.get(payment.method) ?? payment.method}
                      </Text>
                    </div>
                    <Text fw={700}>{formatCurrency(payment.amount_allocated_to_narad)}</Text>
                  </Group>
                  <DetailGrid
                    items={[
                      { label: "Сумма платежа", value: formatCurrency(payment.amount) },
                      { label: "Зачтено в наряд", value: formatCurrency(payment.amount_allocated_to_narad) },
                      { label: "Внешний номер", value: payment.external_reference ?? "—" }
                    ]}
                  />
                  {payment.comment ? (
                    <Text c="dimmed" size="sm">
                      {payment.comment}
                    </Text>
                  ) : null}
                </div>
              ))
            ) : (
              <Text c="dimmed">Платежи по этому наряду пока не распределялись.</Text>
            )}
          </Stack>

          <Divider />
          <Stack gap="sm">
            <Text fw={700}>История статусов</Text>
            {detailQuery.data.status_logs.length ? (
              detailQuery.data.status_logs.map((log) => (
                <div key={log.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>
                    {log.action} · {formatDateTime(log.created_at)}
                  </Text>
                  <Text c="dimmed" size="sm">
                    {log.from_status ? `${log.from_status} → ` : ""}
                    {log.to_status} · {log.actor_email ?? "system"}
                  </Text>
                  {log.note ? (
                    <Text c="dimmed" size="sm">
                      {log.note}
                    </Text>
                  ) : null}
                </div>
              ))
            ) : (
              <Text c="dimmed">История наряда пока пуста.</Text>
            )}
          </Stack>
        </Stack>
      )}
      {detailQuery.data ? (
        <DocumentEmailModal
          opened={emailOpened}
          onClose={emailHandlers.close}
          title="Отправка документа по наряду"
          description={`Отправка счета, акта или печатного наряда по заказу ${detailQuery.data.narad_number}.`}
          defaultKind="invoice"
          defaultRecipientEmail={detailQuery.data.client_email}
          kindOptions={[
            { value: "invoice", label: "Счет" },
            { value: "act", label: "Акт" },
            { value: "job-order", label: "Наряд" }
          ]}
          sendEmail={(payload) => sendNaradDocumentEmail(detailQuery.data.id, payload as NaradDocumentEmailPayload)}
        />
      ) : null}
    </Drawer>
  );
}
