import { notifications } from "@mantine/notifications";

export function showSuccessNotification(message: string, title = "Готово") {
  notifications.show({
    color: "teal",
    title,
    message
  });
}
