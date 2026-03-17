"use client";

import { Button, PasswordInput, Stack, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { login } from "@/entities/auth/api/auth-api";
import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type LoginFormValues = {
  email: string;
  password: string;
};

export function LoginForm() {
  const router = useRouter();
  const { applySession } = useAuthSession();
  const form = useForm<LoginFormValues>({
    initialValues: {
      email: "admin@dentallab.app",
      password: "admin123"
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : "Введите корректный адрес электронной почты."),
      password: (value) => (value.length >= 8 ? null : "Минимум 8 символов.")
    }
  });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess(session) {
      applySession(session);
      showSuccessNotification("Авторизация выполнена.");
      router.push("/works");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось выполнить вход.");
    }
  });

  return (
    <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
      <Stack gap="md">
        <TextInput
          label="Электронная почта"
          placeholder="admin@dentallab.app"
          {...form.getInputProps("email")}
        />
        <PasswordInput label="Пароль" placeholder="Введите пароль" {...form.getInputProps("password")} />
        <Button fullWidth loading={mutation.isPending} size="md" type="submit">
          Войти
        </Button>
        <Button component={Link} fullWidth href="/register" radius="xl" variant="subtle">
          Перейти к регистрации
        </Button>
      </Stack>
    </form>
  );
}
