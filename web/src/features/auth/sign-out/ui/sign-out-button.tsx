"use client";

import { Button } from "@mantine/core";
import { IconLogout } from "@tabler/icons-react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { logout } from "@/entities/auth/api/auth-api";
import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";

export function SignOutButton() {
  const router = useRouter();
  const { clearSession } = useAuthSession();
  const mutation = useMutation({
    mutationFn: logout,
    onSettled() {
      clearSession();
      router.push("/login");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось завершить сессию на сервере.");
    }
  });

  return (
    <Button
      color="gray"
      leftSection={<IconLogout size={16} />}
      loading={mutation.isPending}
      radius="xl"
      variant="light"
      onClick={() => mutation.mutate()}
    >
      Выйти
    </Button>
  );
}
