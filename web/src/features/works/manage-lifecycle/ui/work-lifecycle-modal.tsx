"use client";

import { Button, Group, Modal, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { closeWork, reopenWork } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { WorkCompact, workStatusOptions } from "@/entities/works/model/types";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type WorkLifecycleModalProps = {
  mode: "close" | "reopen";
  opened: boolean;
  onClose: () => void;
  work?: WorkCompact | null;
};

type WorkLifecycleFormValues = {
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

function buildInitialValues(mode: "close" | "reopen", work?: WorkCompact | null): WorkLifecycleFormValues {
  if (mode === "close") {
    return {
      status:
        work?.status && closeStatusOptions.some((item) => item.value === work.status)
          ? work.status
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

export function WorkLifecycleModal({ mode, opened, onClose, work }: WorkLifecycleModalProps) {
  const queryClient = useQueryClient();
  const syncedKeyRef = useRef<string | null>(null);
  const form = useForm<WorkLifecycleFormValues>({
    initialValues: buildInitialValues(mode, work)
  });

  useEffect(() => {
    if (!opened) {
      syncedKeyRef.current = null;
      return;
    }

    const nextKey = `${mode}:${work?.id ?? "new"}:${work?.status ?? "new"}`;
    if (syncedKeyRef.current === nextKey) {
      return;
    }

    syncedKeyRef.current = nextKey;
    form.setValues(buildInitialValues(mode, work));
  }, [form, mode, opened, work]);

  const mutation = useMutation({
    mutationFn: () => {
      if (!work) {
        throw new Error("Работа не выбрана.");
      }

      if (mode === "close") {
        return closeWork(work.id, {
          status: form.values.status as never,
          completed_at: toIsoDateTime(form.values.completed_at),
          ...(form.values.note.trim() ? { note: form.values.note.trim() } : {})
        });
      }

      return reopenWork(work.id, {
        status: form.values.status as never,
        ...(form.values.note.trim() ? { note: form.values.note.trim() } : {})
      });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification(mode === "close" ? "Заказ закрыт." : "Заказ снова открыт.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, mode === "close" ? "Не удалось закрыть заказ." : "Не удалось открыть заказ.");
    }
  });

  const statusOptions = mode === "close" ? closeStatusOptions : reopenStatusOptions;

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={mode === "close" ? "Закрытие заказа" : "Повторное открытие заказа"}
    >
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          <Select
            data={statusOptions.map((item) => ({ value: item.value, label: item.label }))}
            label={mode === "close" ? "Финальный статус" : "Статус после открытия"}
            value={form.values.status}
            onChange={(value) =>
              form.setFieldValue(
                "status",
                value ?? (mode === "close" ? "completed" : "in_progress")
              )
            }
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
            placeholder={mode === "close" ? "Например: передано в расчет зарплаты" : "Например: возвращено на доработку"}
            {...form.getInputProps("note")}
          />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button disabled={!work} loading={mutation.isPending} type="submit">
              {mode === "close" ? "Закрыть" : "Открыть"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
