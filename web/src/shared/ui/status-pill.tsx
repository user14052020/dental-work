import { Badge } from "@mantine/core";

const workStatusMeta: Record<string, { color: string; label: string }> = {
  new: { color: "blue", label: "Новая" },
  in_progress: { color: "teal", label: "В работе" },
  in_review: { color: "yellow", label: "На проверке" },
  completed: { color: "green", label: "Завершена" },
  delivered: { color: "grape", label: "Выдана" },
  cancelled: { color: "red", label: "Отменена" }
};

type StatusPillProps = {
  value: string | boolean | null | undefined;
  kind?: "work" | "boolean";
};

export function StatusPill({ value, kind = "work" }: StatusPillProps) {
  if (kind === "boolean") {
    const active = Boolean(value);

    return (
      <Badge color={active ? "teal" : "gray"} radius="xl" variant="light">
        {active ? "Активен" : "Неактивен"}
      </Badge>
    );
  }

  const meta = workStatusMeta[String(value)] ?? { color: "gray", label: String(value ?? "—") };

  return (
    <Badge color={meta.color} radius="xl" variant="light">
      {meta.label}
    </Badge>
  );
}
