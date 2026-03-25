"use client";

import { Button, Group, Modal, Stack, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useEffect, useRef } from "react";

import { ActualMaterialConsumptionReportItem } from "@/entities/reports/model/types";

type EditActualConsumptionModalProps = {
  entry?: ActualMaterialConsumptionReportItem | null;
  opened: boolean;
  loading?: boolean;
  onClose: () => void;
  onSubmit: (payload: { quantity: string; reason?: string }) => void;
};

export function EditActualConsumptionModal({
  entry,
  opened,
  loading = false,
  onClose,
  onSubmit
}: EditActualConsumptionModalProps) {
  const syncedEntryKeyRef = useRef<string | null>(null);
  const form = useForm({
    initialValues: {
      quantity: "",
      reason: ""
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedEntryKeyRef.current = null;
      return;
    }

    const nextSyncKey = entry?.movement_id ?? "new";
    if (syncedEntryKeyRef.current === nextSyncKey) {
      return;
    }

    syncedEntryKeyRef.current = nextSyncKey;
    const nextValues = {
      quantity: entry?.quantity ?? "",
      reason: entry?.reason ?? ""
    };
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [entry, form, opened]);

  return (
    <Modal opened={opened} onClose={onClose} centered title="Изменить списание по факту">
      <form
        onSubmit={form.onSubmit((values) =>
          onSubmit({
            quantity: values.quantity,
            ...(values.reason.trim() ? { reason: values.reason.trim() } : {})
          })
        )}
      >
        <Stack gap="md">
          <TextInput
            label="Количество"
            type="number"
            step="0.001"
            {...form.getInputProps("quantity")}
          />
          <Textarea
            label="Причина"
            minRows={3}
            placeholder="Например: выдача технику, коррекция склада, расход инструмента"
            {...form.getInputProps("reason")}
          />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={loading} type="submit">
              Сохранить
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
