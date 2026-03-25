"use client";

import {
  Button,
  Divider,
  Group,
  Loader,
  Modal,
  Select,
  Stack,
  Text,
  TextInput,
  Textarea
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import {
  createPayment,
  deletePaymentUnallocatedBalance,
  returnPaymentNaradAllocation,
  updatePayment
} from "@/entities/payments/api/payments-api";
import { paymentsQueryKeys } from "@/entities/payments/model/query-keys";
import {
  PaymentCompact,
  PaymentCreatePayload,
  PaymentMethod,
  paymentMethodOptions
} from "@/entities/payments/model/types";
import {
  usePaymentDetailQuery,
  usePaymentNaradCandidatesQuery
} from "@/entities/payments/model/use-payments-query";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type PaymentFormValues = {
  payment_number: string;
  client_id: string;
  payment_date: string;
  method: PaymentMethod;
  amount: string;
  external_reference: string;
  comment: string;
  allocations: Record<string, string>;
};

const emptyValues: PaymentFormValues = {
  payment_number: "",
  client_id: "",
  payment_date: toDateTimeLocal(new Date().toISOString()),
  method: "bank_transfer",
  amount: "0",
  external_reference: "",
  comment: "",
  allocations: {}
};

function buildPayload(values: PaymentFormValues): PaymentCreatePayload {
  return {
    ...(values.payment_number.trim() ? { payment_number: values.payment_number.trim() } : {}),
    client_id: values.client_id,
    payment_date: toIsoDateTime(values.payment_date) as string,
    method: values.method,
    amount: values.amount || "0",
    ...(values.external_reference.trim() ? { external_reference: values.external_reference.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {}),
    narad_allocations: Object.entries(values.allocations)
      .map(([work_id, amount]) => ({
        narad_id: work_id,
        amount: amount.trim()
      }))
      .filter((item) => Number(item.amount || 0) > 0)
  };
}

function sumAllocations(values: Record<string, string>) {
  const total = Object.values(values).reduce((accumulator, value) => {
    const nextValue = Number(value || 0);
    return accumulator + (Number.isFinite(nextValue) ? nextValue : 0);
  }, 0);
  return total.toFixed(2);
}

type PaymentFormModalProps = {
  payment?: PaymentCompact | null;
  opened: boolean;
  onClose: () => void;
};

export function PaymentFormModal({ payment, opened, onClose }: PaymentFormModalProps) {
  const queryClient = useQueryClient();
  const syncedPaymentKeyRef = useRef<string | null>(null);
  const form = useForm<PaymentFormValues>({
    initialValues: emptyValues,
    validate: {
      client_id: (value) => (value ? null : "Выберите клиента."),
      amount: (value) => (Number(value || 0) > 0 ? null : "Укажите сумму платежа больше нуля.")
    }
  });

  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const paymentDetailQuery = usePaymentDetailQuery(payment?.id);
  const paymentDetail = paymentDetailQuery.data;
  const candidatesQuery = usePaymentNaradCandidatesQuery(form.values.client_id || undefined, payment?.id);

  useEffect(() => {
    if (!opened) {
      syncedPaymentKeyRef.current = null;
      return;
    }

    if (payment && !paymentDetail) {
      return;
    }

    const nextSyncKey = payment ? `${payment.id}:${paymentDetail?.updated_at}` : "new";
    if (syncedPaymentKeyRef.current === nextSyncKey) {
      return;
    }

    syncedPaymentKeyRef.current = nextSyncKey;
    form.setValues(
      payment && paymentDetail
        ? {
            payment_number: paymentDetail.payment_number,
            client_id: paymentDetail.client_id,
            payment_date: toDateTimeLocal(paymentDetail.payment_date),
            method: paymentDetail.method,
            amount: paymentDetail.amount,
            external_reference: paymentDetail.external_reference ?? "",
            comment: paymentDetail.comment ?? "",
            allocations: Object.fromEntries(
              paymentDetail.narad_allocations.map((allocation) => [allocation.narad_id, allocation.amount])
            )
          }
        : emptyValues
    );
  }, [form, opened, payment, paymentDetail]);

  const mutation = useMutation({
    mutationFn: async (values: PaymentFormValues) =>
      payment ? updatePayment(payment.id, buildPayload(values)) : createPayment(buildPayload(values)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: paymentsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification(payment ? "Платеж обновлен." : "Платеж создан.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить платеж.");
    }
  });
  const returnNaradAllocationMutation = useMutation({
    mutationFn: async (naradId: string) => {
      if (!payment) {
        throw new Error("Платеж не выбран.");
      }

      return returnPaymentNaradAllocation(payment.id, { narad_id: naradId });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: paymentsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Сумма по наряду возвращена в нераспределенный остаток платежа.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось вернуть сумму в платеж.");
    }
  });
  const deleteUnallocatedBalanceMutation = useMutation({
    mutationFn: async () => {
      if (!payment) {
        throw new Error("Платеж не выбран.");
      }

      return deletePaymentUnallocatedBalance(payment.id);
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: paymentsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Нераспределенный остаток платежа удален.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось удалить нераспределенный остаток.");
    }
  });

  const clientOptions =
    clientsQuery.data?.items.map((client) => ({
      value: client.id,
      label: client.name
    })) ?? [];

  const allocatedTotal = useMemo(() => sumAllocations(form.values.allocations), [form.values.allocations]);
  const unallocatedTotal = Math.max(Number(form.values.amount || 0) - Number(allocatedTotal), 0).toFixed(2);

  const isLoading = payment ? paymentDetailQuery.isLoading : false;

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      size="xl"
      title={payment ? "Редактирование платежа" : "Новый платеж"}
    >
      {isLoading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
          <Stack gap="md">
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput
                label="Номер платежа"
                placeholder="Автоматически, если не указан"
                {...form.getInputProps("payment_number")}
              />
              <Select
                data={clientOptions}
                label="Клиент"
                placeholder="Выберите клиента"
                value={form.values.client_id || null}
                onChange={(value) => {
                  form.setFieldValue("client_id", value ?? "");
                  form.setFieldValue("allocations", {});
                }}
                error={form.errors.client_id}
              />
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <TextInput
                label="Дата и время"
                type="datetime-local"
                {...form.getInputProps("payment_date")}
              />
              <Select
                data={paymentMethodOptions}
                label="Способ оплаты"
                value={form.values.method}
                onChange={(value) => form.setFieldValue("method", (value as PaymentMethod) ?? "bank_transfer")}
              />
              <TextInput label="Сумма" {...form.getInputProps("amount")} />
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="Внешний номер / ссылка" {...form.getInputProps("external_reference")} />
              <TextInput label="Распределено" value={formatCurrency(allocatedTotal)} readOnly />
            </div>
            <TextInput label="Нераспределенный остаток" value={formatCurrency(unallocatedTotal)} readOnly />
            {payment && Number(unallocatedTotal) > 0 ? (
              <Button
                type="button"
                color="red"
                variant="light"
                loading={deleteUnallocatedBalanceMutation.isPending}
                onClick={() => {
                  if (!window.confirm(`Удалить нераспределенный остаток по платежу ${payment.payment_number}?`)) {
                    return;
                  }
                  deleteUnallocatedBalanceMutation.mutate();
                }}
              >
                Удалить остаток платежа
              </Button>
            ) : null}

            <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />

            <Divider />
            <Stack gap="sm">
              <Text fw={700}>Распределение по нарядам</Text>
              {!form.values.client_id ? (
                <Text c="dimmed">Сначала выберите клиента, чтобы увидеть доступные наряды.</Text>
              ) : candidatesQuery.isLoading ? (
                <Group justify="center" py="sm">
                  <Loader size="sm" />
                </Group>
              ) : candidatesQuery.data?.length ? (
                candidatesQuery.data.map((narad) => (
                  <div key={narad.narad_id} className="rounded-[20px] bg-slate-50 px-4 py-4">
                    <div className="grid gap-3 md:grid-cols-[1.6fr_220px] md:items-end">
                      <div>
                        <Text fw={700}>
                          {narad.narad_number} · {narad.title}
                        </Text>
                        <Text c="dimmed" mt={4} size="sm">
                          Работ в наряде: {narad.works_count} · остаток: {formatCurrency(narad.balance_due)} · доступно к распределению:{" "}
                          {formatCurrency(narad.available_to_allocate)}
                        </Text>
                      </div>
                      <Stack gap="xs">
                        <TextInput
                          label="Сумма распределения"
                          value={form.values.allocations[narad.narad_id] ?? ""}
                          onChange={(event) =>
                            form.setFieldValue("allocations", {
                              ...form.values.allocations,
                              [narad.narad_id]: event.currentTarget.value
                            })
                          }
                        />
                        {payment && Number(narad.existing_allocation_amount) > 0 ? (
                          <Button
                            type="button"
                            color="orange"
                            variant="subtle"
                            loading={
                              returnNaradAllocationMutation.isPending &&
                              returnNaradAllocationMutation.variables === narad.narad_id
                            }
                            onClick={() => {
                              if (
                                !window.confirm(
                                  `Вернуть ${formatCurrency(narad.existing_allocation_amount)} из наряда ${narad.narad_number} обратно в платеж?`
                                )
                              ) {
                                return;
                              }
                              returnNaradAllocationMutation.mutate(narad.narad_id);
                            }}
                          >
                            Вернуть в платеж
                          </Button>
                        ) : null}
                      </Stack>
                    </div>
                  </div>
                ))
              ) : (
                <Text c="dimmed">Для выбранного клиента нет нарядов с доступным остатком к оплате.</Text>
              )}
            </Stack>

            <Button loading={mutation.isPending} type="submit">
              {payment ? "Сохранить" : "Создать"}
            </Button>
          </Stack>
        </form>
      )}
    </Modal>
  );
}
