"use client";

import { Button, ButtonProps } from "@mantine/core";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteClient } from "@/entities/clients/api/clients-api";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type DeleteClientButtonProps = ButtonProps & {
  clientId: string;
  onDeleted?: () => void;
};

export function DeleteClientButton({ clientId, onDeleted, ...props }: DeleteClientButtonProps) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => deleteClient(clientId),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      showSuccessNotification("Клиент удален.");
      onDeleted?.();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось удалить клиента.");
    }
  });

  return (
    <Button
      color="red"
      loading={mutation.isPending}
      variant="light"
      onClick={() => {
        if (window.confirm("Удалить клиента без возможности восстановления?")) {
          mutation.mutate();
        }
      }}
      {...props}
    >
      Удалить
    </Button>
  );
}
