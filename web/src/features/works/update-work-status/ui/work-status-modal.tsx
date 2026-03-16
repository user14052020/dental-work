"use client";

import { Button, Group, Modal, Select, Stack, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { updateWorkStatus } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { WorkCompact, workStatusOptions } from "@/entities/works/model/types";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type WorkStatusModalProps = {
  work?: WorkCompact | null;
  opened: boolean;
  onClose: () => void;
};

type WorkStatusFormValues = {
  status: string;
  completed_at: string;
};

export function WorkStatusModal({ work, opened, onClose }: WorkStatusModalProps) {
  const queryClient = useQueryClient();
  const form = useForm<WorkStatusFormValues>({
    initialValues: {
      status: work?.status ?? "new",
      completed_at: ""
    }
  });

  useEffect(() => {
    form.setValues({
      status: work?.status ?? "new",
      completed_at: ""
    });
  }, [form, work]);

  const mutation = useMutation({
    mutationFn: () =>
      updateWorkStatus(work?.id as string, {
        status: form.values.status as never,
        completed_at: toIsoDateTime(form.values.completed_at)
      }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Статус работы обновлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось обновить статус.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} title="Изменение статуса работы">
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          <Select
            data={workStatusOptions.map((status) => ({ value: status.value, label: status.label }))}
            label="Статус"
            value={form.values.status}
            onChange={(value) => form.setFieldValue("status", value ?? "new")}
          />
          <TextInput
            label="Дата завершения"
            placeholder={toDateTimeLocal(new Date().toISOString())}
            type="datetime-local"
            {...form.getInputProps("completed_at")}
          />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button disabled={!work} loading={mutation.isPending} type="submit">
              Обновить
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
