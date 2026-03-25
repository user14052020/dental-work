"use client";

import { Button, Group, Modal, NumberInput, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { useContractorsQuery } from "@/entities/contractors/model/use-contractors-query";
import { markOutsideWorkReturned, markOutsideWorkSent } from "@/entities/narads/api/narads-api";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { OutsideWorkItem } from "@/entities/narads/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type OutsideWorkStatusModalProps = {
  item?: OutsideWorkItem | null;
  mode: "sent" | "returned";
  opened: boolean;
  onClose: () => void;
};

type OutsideWorkStatusValues = {
  contractor_id: string;
  outside_order_number: string;
  outside_cost: string;
  outside_sent_at: string;
  outside_due_at: string;
  outside_returned_at: string;
  outside_comment: string;
};

function buildInitialValues(item?: OutsideWorkItem | null): OutsideWorkStatusValues {
  return {
    contractor_id: item?.contractor_id ?? "",
    outside_order_number: item?.outside_order_number ?? "",
    outside_cost: item?.outside_cost ?? "0",
    outside_sent_at: item?.outside_sent_at ? item.outside_sent_at.slice(0, 16) : new Date().toISOString().slice(0, 16),
    outside_due_at: item?.outside_due_at ? item.outside_due_at.slice(0, 16) : "",
    outside_returned_at: item?.outside_returned_at
      ? item.outside_returned_at.slice(0, 16)
      : new Date().toISOString().slice(0, 16),
    outside_comment: item?.outside_comment ?? ""
  };
}

export function OutsideWorkStatusModal({ item, mode, opened, onClose }: OutsideWorkStatusModalProps) {
  const queryClient = useQueryClient();
  const syncKeyRef = useRef<string | null>(null);
  const contractorsQuery = useContractorsQuery({
    page: 1,
    page_size: 100,
    active_only: true
  });
  const form = useForm<OutsideWorkStatusValues>({
    initialValues: buildInitialValues(item),
    validate:
      mode === "sent"
        ? {
            contractor_id: (value) => (value ? null : "Выбери подрядчика.")
          }
        : {}
  });
  const contractorOptions = (contractorsQuery.data?.items ?? []).map((contractor) => ({
    value: contractor.id,
    label: contractor.name
  }));
  const selectedContractor =
    contractorsQuery.data?.items.find((contractor) => contractor.id === form.values.contractor_id) ?? null;

  useEffect(() => {
    if (!opened) {
      syncKeyRef.current = null;
      return;
    }
    const nextKey = `${mode}:${item?.narad_id ?? "new"}:${item?.outside_sent_at ?? ""}:${item?.outside_returned_at ?? ""}`;
    if (syncKeyRef.current === nextKey) {
      return;
    }
    syncKeyRef.current = nextKey;
    const nextValues = buildInitialValues(item);
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [form, item, mode, opened]);

  const mutation = useMutation({
    mutationFn: () => {
      if (!item) {
        throw new Error("narad is required");
      }
      if (mode === "sent") {
        return markOutsideWorkSent(item.narad_id, {
          contractor_id: form.values.contractor_id,
          outside_order_number: form.values.outside_order_number.trim() || undefined,
          outside_cost: form.values.outside_cost || "0",
          outside_sent_at: new Date(form.values.outside_sent_at).toISOString(),
          outside_due_at: form.values.outside_due_at ? new Date(form.values.outside_due_at).toISOString() : undefined,
          outside_comment: form.values.outside_comment.trim() || undefined
        });
      }
      return markOutsideWorkReturned(item.narad_id, {
        outside_returned_at: new Date(form.values.outside_returned_at).toISOString(),
        outside_comment: form.values.outside_comment.trim() || undefined
      });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      showSuccessNotification(mode === "sent" ? "Наряд отправлен на сторону." : "Наряд возвращен со стороны.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, mode === "sent" ? "Не удалось отправить наряд на сторону." : "Не удалось отметить возврат.");
    }
  });

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={mode === "sent" ? "Отправить на сторону" : "Вернуть со стороны"}
      size="lg"
    >
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          {mode === "sent" ? (
            <>
              <Group grow>
                <Select
                  data={contractorOptions}
                  label="Подрядчик"
                  placeholder="Выберите подрядчика"
                  required
                  searchable
                  value={form.values.contractor_id || null}
                  onChange={(value) => form.setFieldValue("contractor_id", value ?? "")}
                />
                <TextInput label="Внешний номер" {...form.getInputProps("outside_order_number")} />
              </Group>
              <Group grow>
                <TextInput label="Контактное лицо" readOnly value={selectedContractor?.contact_person ?? ""} />
                <TextInput label="Телефон подрядчика" readOnly value={selectedContractor?.phone ?? ""} />
              </Group>
              <Group grow>
                <NumberInput
                  label="Стоимость на стороне"
                  decimalScale={2}
                  hideControls
                  min={0}
                  step={0.01}
                  value={form.values.outside_cost}
                  onChange={(value) => form.setFieldValue("outside_cost", String(value ?? ""))}
                />
                <TextInput label="Дата отправки" type="datetime-local" required {...form.getInputProps("outside_sent_at")} />
                <TextInput label="Вернуть до" type="datetime-local" {...form.getInputProps("outside_due_at")} />
              </Group>
            </>
          ) : (
            <TextInput
              label="Дата возврата"
              type="datetime-local"
              required
              {...form.getInputProps("outside_returned_at")}
            />
          )}
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("outside_comment")} />

          <Group justify="flex-end">
            <Button variant="default" onClick={onClose}>
              Отмена
            </Button>
            <Button type="submit" loading={mutation.isPending}>
              {mode === "sent" ? "Сохранить отправку" : "Сохранить возврат"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
