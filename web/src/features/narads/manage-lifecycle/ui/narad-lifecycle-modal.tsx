"use client";

import { Button, Group, Modal, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { closeNarad, reopenNarad } from "@/entities/narads/api/narads-api";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { NaradCompact } from "@/entities/narads/model/types";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { workStatusOptions } from "@/entities/works/model/types";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type NaradLifecycleModalProps = {
  mode: "close" | "reopen";
  opened: boolean;
  onClose: () => void;
  narad?: NaradCompact | null;
};

type NaradLifecycleFormValues = {
  status: string;
  completed_at: string;
  note: string;
};

const closeStatusOptions = workStatusOptions.filter((item) =>
  ["completed", "delivered", "cancelled"].includes(item.value)
);
const reopenStatusOptions = workStatusOptions.filter((item) =>
  ["new", "in_progress", "in_review"].includes(item.value)
);

function buildInitialValues(mode: "close" | "reopen", narad?: NaradCompact | null): NaradLifecycleFormValues {
  if (mode === "close") {
    return {
      status:
        narad?.status && closeStatusOptions.some((item) => item.value === narad.status)
          ? narad.status
          : "completed",
      completed_at: toDateTimeLocal(new Date().toISOString()),
      note: ""
    };
  }

  return {
    status: "in_progress",
    completed_at: "",
    note: ""
  };
}

export function NaradLifecycleModal({ mode, opened, onClose, narad }: NaradLifecycleModalProps) {
  const queryClient = useQueryClient();
  const syncedKeyRef = useRef<string | null>(null);
  const form = useForm<NaradLifecycleFormValues>({
    initialValues: buildInitialValues(mode, narad)
  });

  useEffect(() => {
    if (!opened) {
      syncedKeyRef.current = null;
      return;
    }

    const nextKey = `${mode}:${narad?.id ?? "new"}:${narad?.status ?? "new"}`;
    if (syncedKeyRef.current === nextKey) {
      return;
    }

    syncedKeyRef.current = nextKey;
    form.setValues(buildInitialValues(mode, narad));
  }, [form, mode, narad, opened]);

  const mutation = useMutation({
    mutationFn: () => {
      if (!narad) {
        throw new Error("Наряд не выбран.");
      }

      if (mode === "close") {
        return closeNarad(narad.id, {
          status: form.values.status as "completed" | "delivered" | "cancelled",
          completed_at: toIsoDateTime(form.values.completed_at) ?? undefined,
          ...(form.values.note.trim() ? { note: form.values.note.trim() } : {})
        });
      }

      return reopenNarad(narad.id, {
        status: form.values.status as "new" | "in_progress" | "in_review",
        ...(form.values.note.trim() ? { note: form.values.note.trim() } : {})
      });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification(mode === "close" ? "Наряд закрыт." : "Наряд снова открыт.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, mode === "close" ? "Не удалось закрыть наряд." : "Не удалось открыть наряд.");
    }
  });

  const statusOptions = mode === "close" ? closeStatusOptions : reopenStatusOptions;

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={mode === "close" ? "Закрытие наряда" : "Повторное открытие наряда"}
    >
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          <Select
            data={statusOptions.map((item) => ({ value: item.value, label: item.label }))}
            label={mode === "close" ? "Финальный статус" : "Статус после открытия"}
            value={form.values.status}
            onChange={(value) => form.setFieldValue("status", value ?? (mode === "close" ? "completed" : "in_progress"))}
          />
          {mode === "close" ? (
            <TextInput
              label="Дата завершения"
              placeholder={toDateTimeLocal(new Date().toISOString())}
              type="datetime-local"
              {...form.getInputProps("completed_at")}
            />
          ) : null}
          <Textarea
            label="Комментарий"
            minRows={3}
            placeholder={mode === "close" ? "Например: передано в архив и склад списан" : "Например: возвращено в производство"}
            {...form.getInputProps("note")}
          />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button disabled={!narad} loading={mutation.isPending} type="submit">
              {mode === "close" ? "Закрыть" : "Открыть"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
