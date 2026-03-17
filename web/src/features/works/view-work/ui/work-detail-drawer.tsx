"use client";

import {
  Button,
  Divider,
  Drawer,
  Group,
  Loader,
  Select,
  Stack,
  Text
} from "@mantine/core";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconFileInvoice, IconFileText, IconPrinter } from "@tabler/icons-react";

import {
  operationExecutionStatusOptions,
  OperationExecutionStatus
} from "@/entities/operations/model/types";
import { updateWorkOperationStatus } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { faceShapeOptions, patientGenderOptions } from "@/entities/works/model/types";
import { useWorkDetailQuery } from "@/entities/works/model/use-works-query";
import { WorkAttachmentsSection } from "@/features/works/manage-attachments/ui/work-attachments-section";
import { Odontogram } from "@/entities/works/ui/odontogram";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";
import { DetailGrid } from "@/shared/ui/detail-grid";
import { StatusPill } from "@/shared/ui/status-pill";

type WorkDetailDrawerProps = {
  workId?: string;
  opened: boolean;
  onClose: () => void;
  onCloseWork?: () => void;
  onReopenWork?: () => void;
  onStatusChange?: () => void;
};

function openPrintDocument(path: string) {
  if (typeof window === "undefined") {
    return;
  }

  window.open(path, "_blank", "noopener,noreferrer");
}

const patientGenderLabels = Object.fromEntries(
  patientGenderOptions.map((option) => [option.value, option.label])
) as Record<string, string>;
const faceShapeLabels = Object.fromEntries(faceShapeOptions.map((option) => [option.value, option.label])) as Record<
  string,
  string
>;

export function WorkDetailDrawer({
  workId,
  opened,
  onClose,
  onCloseWork,
  onReopenWork,
  onStatusChange
}: WorkDetailDrawerProps) {
  const queryClient = useQueryClient();
  const detailQuery = useWorkDetailQuery(workId);
  const patientGenderLabel = detailQuery.data?.patient_gender
    ? patientGenderLabels[detailQuery.data.patient_gender] ?? detailQuery.data.patient_gender
    : "—";
  const faceShapeLabel = detailQuery.data?.face_shape
    ? faceShapeLabels[detailQuery.data.face_shape] ?? detailQuery.data.face_shape
    : "—";

  const operationStatusMutation = useMutation({
    mutationFn: ({
      workOperationId,
      status
    }: {
      workOperationId: string;
      status: OperationExecutionStatus;
    }) => updateWorkOperationStatus(workId as string, workOperationId, { status }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Статус операции обновлен.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось обновить статус операции.");
    }
  });

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
                {detailQuery.data.work_catalog_item_code ? ` · ${detailQuery.data.work_catalog_item_code}` : ""}
              </Text>
            </div>
            <StatusPill value={detailQuery.data.status} />
          </Group>

          <Group gap="sm" wrap="wrap">
            <Button
              leftSection={<IconFileInvoice size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/works/${detailQuery.data.id}/invoice`)}
            >
              Счет
            </Button>
            <Button
              leftSection={<IconFileText size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/works/${detailQuery.data.id}/act`)}
            >
              Акт
            </Button>
            <Button
              leftSection={<IconPrinter size={16} />}
              variant="light"
              onClick={() => openPrintDocument(`/api/proxy/documents/works/${detailQuery.data.id}/job-order`)}
            >
              Наряд
            </Button>
          </Group>

          <DetailGrid
            items={[
              { label: "Клиент", value: detailQuery.data.client_name },
              { label: "Исполнитель", value: detailQuery.data.executor_name ?? "—" },
              {
                label: "Каталог работ",
                value: detailQuery.data.work_catalog_item_name
                  ? `${detailQuery.data.work_catalog_item_code ?? "—"} · ${detailQuery.data.work_catalog_item_name}`
                  : "—"
              },
              { label: "Категория работы", value: detailQuery.data.work_catalog_item_category ?? "—" },
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
              { label: "Принята", value: formatDateTime(detailQuery.data.received_at) },
              { label: "Дедлайн", value: formatDateTime(detailQuery.data.deadline_at) },
              { label: "Завершена", value: formatDateTime(detailQuery.data.completed_at) },
              { label: "Закрыта", value: formatDateTime(detailQuery.data.closed_at) },
              { label: "Отправлена доставкой", value: detailQuery.data.delivery_sent ? "Да" : "Нет" },
              { label: "Дата отправки", value: formatDateTime(detailQuery.data.delivery_sent_at) },
              { label: "Базовая цена", value: formatCurrency(detailQuery.data.base_price_for_client) },
              { label: "Скидка / надбавка, %", value: detailQuery.data.price_adjustment_percent },
              { label: "Цена клиенту", value: formatCurrency(detailQuery.data.price_for_client) },
              { label: "Себестоимость", value: formatCurrency(detailQuery.data.cost_price) },
              { label: "Маржа", value: formatCurrency(detailQuery.data.margin) },
              { label: "Оплата технику", value: formatCurrency(detailQuery.data.labor_cost) },
              { label: "Оплачено", value: formatCurrency(detailQuery.data.amount_paid) },
              { label: "Остаток к оплате", value: formatCurrency(detailQuery.data.balance_due) },
              { label: "Доп. расходы", value: formatCurrency(detailQuery.data.additional_expenses) },
              { label: "Трудозатраты", value: detailQuery.data.labor_hours }
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
            <Group justify="space-between" align="center">
              <Text fw={700}>Позиции заказа</Text>
              <Text c="dimmed" size="sm">
                {detailQuery.data.work_items.length
                  ? `${detailQuery.data.work_items.length} строк(и)`
                  : "Позиции заказа не сформированы"}
              </Text>
            </Group>
            {detailQuery.data.work_items.length ? (
              detailQuery.data.work_items.map((item) => (
                <div key={item.id} className="rounded-[20px] bg-slate-50 px-4 py-4">
                  <Group justify="space-between" align="start" wrap="wrap">
                    <div>
                      <Text fw={700}>
                        {item.work_catalog_item_code ? `${item.work_catalog_item_code} · ` : ""}
                        {item.work_type}
                      </Text>
                      <Text c="dimmed" mt={4} size="sm">
                        {item.work_catalog_item_category ?? "Без категории"}
                        {item.work_catalog_item_name ? ` · ${item.work_catalog_item_name}` : ""}
                      </Text>
                    </div>
                    <Text fw={700}>{formatCurrency(item.total_price)}</Text>
                  </Group>
                  {item.description ? (
                    <Text c="dimmed" mt={10} size="sm">
                      {item.description}
                    </Text>
                  ) : null}
                  <DetailGrid
                    items={[
                      { label: "Количество", value: item.quantity },
                      { label: "Цена за ед.", value: formatCurrency(item.unit_price) },
                      { label: "Итого", value: formatCurrency(item.total_price) }
                    ]}
                  />
                </div>
              ))
            ) : (
              <Text c="dimmed">В этой работе пока нет отдельных строк заказа.</Text>
            )}
          </Stack>

          {detailQuery.data.tooth_selection.length ? (
            <>
              <Divider />
              <Stack gap="sm">
                <Text fw={700}>Графическая зубная формула</Text>
                <Odontogram readOnly value={detailQuery.data.tooth_selection} />
              </Stack>
            </>
          ) : null}

          <Divider />
          <Stack gap="sm">
            <Group justify="space-between" align="center">
              <Text fw={700}>Производственные операции</Text>
              <Text c="dimmed" size="sm">
                {detailQuery.data.operations.length
                  ? `${detailQuery.data.operations.length} строк(и)`
                  : "Операции пока не добавлены"}
              </Text>
            </Group>
            {detailQuery.data.operations.length ? (
              detailQuery.data.operations.map((operation) => (
                <div key={operation.id} className="rounded-[20px] bg-slate-50 px-4 py-4">
                  <div className="grid gap-4 md:grid-cols-[1.5fr_220px] md:items-start">
                    <div>
                      <Group gap="sm" wrap="wrap">
                        <Text fw={700}>
                          {operation.operation_code ? `${operation.operation_code} · ` : ""}
                          {operation.operation_name}
                        </Text>
                        <StatusPill kind="operation" value={operation.status} />
                      </Group>
                      <Text c="dimmed" mt={4} size="sm">
                        {operation.executor_name ?? "Исполнитель не назначен"} ·{" "}
                        {operation.executor_category_name ?? "Категория оплаты не назначена"}
                      </Text>
                    </div>
                    <Select
                      data={operationExecutionStatusOptions.map((item) => ({
                        value: item.value,
                        label: item.label
                      }))}
                      label="Статус операции"
                      value={operation.status}
                      onChange={(value) => {
                        if (!value || value === operation.status) {
                          return;
                        }

                        operationStatusMutation.mutate({
                          workOperationId: operation.id,
                          status: value as OperationExecutionStatus
                        });
                      }}
                    />
                  </div>

                  <DetailGrid
                    items={[
                      { label: "Количество", value: operation.quantity },
                      { label: "Ставка", value: formatCurrency(operation.unit_labor_cost) },
                      { label: "Итого", value: formatCurrency(operation.total_labor_cost) },
                      { label: "Ручная ставка", value: operation.manual_rate_override ? "Да" : "Нет" }
                    ]}
                  />

                  {operation.note ? (
                    <div className="mt-3">
                      <Text c="dimmed" size="sm">
                        Примечание
                      </Text>
                      <Text mt={6}>{operation.note}</Text>
                    </div>
                  ) : null}
                </div>
              ))
            ) : (
              <Text c="dimmed">Для этой работы производственные операции пока не заданы.</Text>
            )}
          </Stack>

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

          <Divider />
          <WorkAttachmentsSection attachments={detailQuery.data.attachments} workId={detailQuery.data.id} />

          <Divider />
          <Stack gap="sm">
            <Text fw={700}>Журнал изменений</Text>
            {detailQuery.data.change_logs.length ? (
              detailQuery.data.change_logs.map((log) => (
                <div key={log.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
                  <Text fw={600}>
                    {log.action} · {formatDateTime(log.created_at)}
                  </Text>
                  <Text c="dimmed" size="sm">
                    {log.actor_email ?? "system"}
                  </Text>
                </div>
              ))
            ) : (
              <Text c="dimmed">История изменений пока пуста.</Text>
            )}
          </Stack>

          {onStatusChange ? (
            <Group justify="flex-end">
              {detailQuery.data.closed_at && onReopenWork ? (
                <Button color="blue" variant="light" onClick={onReopenWork}>
                  Открыть заказ
                </Button>
              ) : !detailQuery.data.closed_at && onCloseWork ? (
                <Button color="dark" variant="light" onClick={onCloseWork}>
                  Закрыть заказ
                </Button>
              ) : null}
              <Button variant="light" onClick={onStatusChange}>
                Изменить статус заказа
              </Button>
            </Group>
          ) : null}
        </Stack>
      )}
    </Drawer>
  );
}
