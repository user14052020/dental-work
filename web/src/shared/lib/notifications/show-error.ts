import { notifications } from "@mantine/notifications";

import { ApiError } from "@/shared/api/http-client";

export function showErrorNotification(error: unknown, fallbackMessage = "Не удалось выполнить запрос.") {
  const message = error instanceof ApiError ? error.message : fallbackMessage;

  notifications.show({
    color: "red",
    title: "Ошибка",
    message
  });
}
