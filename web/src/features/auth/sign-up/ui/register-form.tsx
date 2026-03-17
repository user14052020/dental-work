"use client";

import { Button, PasswordInput, Stack, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { register } from "@/entities/auth/api/auth-api";
import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type RegisterFormValues = {
  email: string;
  password: string;
  confirmPassword: string;
};

export function RegisterForm() {
  const router = useRouter();
  const { applySession } = useAuthSession();
  const form = useForm<RegisterFormValues>({
    initialValues: {
      email: "",
      password: "",
      confirmPassword: ""
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : "Введите корректный адрес электронной почты."),
      password: (value) => (value.length >= 8 ? null : "Минимум 8 символов."),
      confirmPassword: (value, values) => (value === values.password ? null : "Пароли должны совпадать.")
    }
  });

  const mutation = useMutation({
    mutationFn: register,
    onSuccess(session) {
      applySession(session);
      showSuccessNotification("Учетная запись создана.");
      router.push("/works");
    },
    onError(error) {
      showErrorNotification(error, "Регистрация не удалась.");
    }
  });

  return (
    <form
      onSubmit={form.onSubmit(({ confirmPassword: _confirmPassword, ...values }) => mutation.mutate(values))}
    >
      <Stack gap="md">
        <TextInput
          label="Электронная почта"
          placeholder="owner@klinika.ru"
          {...form.getInputProps("email")}
        />
        <PasswordInput label="Пароль" placeholder="Минимум 8 символов" {...form.getInputProps("password")} />
        <PasswordInput
          label="Повторите пароль"
          placeholder="Повторите пароль"
          {...form.getInputProps("confirmPassword")}
        />
        <Button fullWidth loading={mutation.isPending} size="md" type="submit">
          Создать аккаунт
        </Button>
        <Button component={Link} fullWidth href="/login" radius="xl" variant="subtle">
          Вернуться ко входу
        </Button>
      </Stack>
    </form>
  );
}
