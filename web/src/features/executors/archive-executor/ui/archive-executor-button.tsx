"use client";

import { Button, ButtonProps } from "@mantine/core";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { archiveExecutor } from "@/entities/executors/api/executors-api";
import { executorsQueryKeys } from "@/entities/executors/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ArchiveExecutorButtonProps = ButtonProps & {
  executorId: string;
  onArchived?: () => void;
};

export function ArchiveExecutorButton({
  executorId,
  onArchived,
  ...props
}: ArchiveExecutorButtonProps) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => archiveExecutor(executorId),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: executorsQueryKeys.root });
      showSuccessNotification("Исполнитель архивирован.");
      onArchived?.();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось архивировать исполнителя.");
    }
  });

  return (
    <Button loading={mutation.isPending} variant="light" onClick={() => mutation.mutate()} {...props}>
      Архивировать
    </Button>
  );
}
