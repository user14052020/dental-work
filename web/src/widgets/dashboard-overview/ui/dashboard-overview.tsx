import { Alert, Grid, Group, Loader, List, Stack, Text } from "@mantine/core";
import {
  IconAlertTriangle,
  IconChartBar,
  IconCoin,
  IconFlask2,
  IconReceipt2,
  IconUsers
} from "@tabler/icons-react";

import { DashboardSnapshot } from "@/entities/dashboard/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { KpiCard } from "@/shared/ui/kpi-card";
import { SectionCard } from "@/shared/ui/section-card";

type DashboardOverviewProps = {
  data?: DashboardSnapshot;
  isLoading: boolean;
  isError: boolean;
};

function DashboardTopList({
  title,
  items,
  emptyMessage
}: {
  title: string;
  items: { id: string; label: string; work_count: number; amount: string }[];
  emptyMessage: string;
}) {
  return (
    <SectionCard>
      <Stack gap="md">
        <Text fw={700} size="lg">
          {title}
        </Text>
        {items.length ? (
          <List spacing="sm" withPadding>
            {items.map((item) => (
              <List.Item key={item.id}>
                <Group justify="space-between">
                  <Text>{item.label}</Text>
                  <Text c="dimmed" size="sm">
                    {item.work_count} работ · {formatCurrency(item.amount)}
                  </Text>
                </Group>
              </List.Item>
            ))}
          </List>
        ) : (
          <Text c="dimmed">{emptyMessage}</Text>
        )}
      </Stack>
    </SectionCard>
  );
}

export function DashboardOverview({ data, isLoading, isError }: DashboardOverviewProps) {
  if (isLoading) {
    return (
      <SectionCard>
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      </SectionCard>
    );
  }

  if (isError || !data) {
    return (
      <Alert color="red" title="Сводка недоступна">
        Не удалось загрузить сводные показатели.
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      <Grid>
        <Grid.Col span={{ base: 12, md: 6, xl: 3 }}>
          <KpiCard
            title="Активные работы"
            value={String(data.active_works)}
            hint="Заказы в производственном цикле"
            icon={<IconChartBar size={26} />}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6, xl: 3 }}>
          <KpiCard
            title="Просроченные"
            value={String(data.overdue_works)}
            hint="Требуют приоритизации"
            icon={<IconAlertTriangle size={26} />}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6, xl: 3 }}>
          <KpiCard
            title="Выручка"
            value={formatCurrency(data.revenue)}
            hint="Сумма заказов за период"
            icon={<IconReceipt2 size={26} />}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6, xl: 3 }}>
          <KpiCard
            title="Прибыль"
            value={formatCurrency(data.profit)}
            hint="После вычета материалов и труда"
            icon={<IconCoin size={26} />}
          />
        </Grid.Col>
      </Grid>

      <Grid>
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <SectionCard>
            <Stack gap="md">
              <Text fw={700} size="lg">
                Финансовый срез
              </Text>
              <Group grow>
                <div className="rounded-[22px] bg-white/70 p-5">
                  <Text c="dimmed" size="sm">
                    Материальные расходы
                  </Text>
                  <Text fw={800} mt={8} size="1.8rem">
                    {formatCurrency(data.material_expenses)}
                  </Text>
                </div>
                <div className="rounded-[22px] bg-white/70 p-5">
                  <Text c="dimmed" size="sm">
                    Сгенерировано
                  </Text>
                  <Text fw={800} mt={8} size="1.2rem">
                    {formatDateTime(data.generated_at)}
                  </Text>
                </div>
              </Group>
            </Stack>
          </SectionCard>
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <SectionCard>
            <Stack gap="md">
              <Text fw={700} size="lg">
                Быстрый обзор
              </Text>
              <Group grow>
                <div className="rounded-[22px] bg-white/70 p-5">
                  <Group gap="xs">
                    <IconUsers size={18} />
                    <Text fw={600}>Клиенты</Text>
                  </Group>
                  <Text c="dimmed" mt={6} size="sm">
                    Топ по объему заказов и повторным работам.
                  </Text>
                </div>
                <div className="rounded-[22px] bg-white/70 p-5">
                  <Group gap="xs">
                    <IconFlask2 size={18} />
                    <Text fw={600}>Материалы</Text>
                  </Group>
                  <Text c="dimmed" mt={6} size="sm">
                    Контроль расхода и низких остатков вынесен в отдельный экран.
                  </Text>
                </div>
              </Group>
            </Stack>
          </SectionCard>
        </Grid.Col>
      </Grid>

      <Grid>
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <DashboardTopList
            title="Топ клиентов"
            emptyMessage="Пока нет данных по клиентам."
            items={data.top_clients.map((item) => ({
              id: item.id,
              label: item.name ?? "Без названия",
              work_count: item.work_count,
              amount: item.amount
            }))}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <DashboardTopList
            title="Топ исполнителей"
            emptyMessage="Пока нет данных по исполнителям."
            items={data.top_executors.map((item) => ({
              id: item.id,
              label: item.full_name ?? "Без имени",
              work_count: item.work_count,
              amount: item.amount
            }))}
          />
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
