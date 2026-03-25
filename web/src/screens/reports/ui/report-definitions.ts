import {
  IconAlertTriangle,
  IconClipboardList,
  IconFiles,
  IconFlask2,
  IconFlask,
  IconReceipt2,
  IconReportAnalytics,
  IconStack2,
  IconUsers
} from "@tabler/icons-react";

export type ReportDefinition = {
  href: string;
  title: string;
  description: string;
  icon: typeof IconReportAnalytics;
};

export const reportDefinitions: ReportDefinition[] = [
  {
    href: "/reports",
    title: "Каталог отчетов",
    description: "Сводка метрик и быстрый вход в отдельные аналитические отчеты.",
    icon: IconReportAnalytics
  },
  {
    href: "/reports/client-balances",
    title: "Баланс клиентов",
    description: "Задолженность, объем заказов и последняя активность по клиентам.",
    icon: IconReceipt2
  },
  {
    href: "/reports/narads",
    title: "Реестр нарядов",
    description: "Финансовый и производственный срез по заказам на уровне наряда.",
    icon: IconFiles
  },
  {
    href: "/reports/executors",
    title: "Исполнители",
    description: "Текущая загрузка, закрытые работы и начисленный труд.",
    icon: IconUsers
  },
  {
    href: "/reports/payroll",
    title: "Оплата труда",
    description: "Начисления техникам по операциям в закрытых нарядах.",
    icon: IconStack2
  },
  {
    href: "/reports/payroll-operations",
    title: "Операции по нарядам",
    description: "Детализация начислений по техникам и конкретным операциям.",
    icon: IconClipboardList
  },
  {
    href: "/reports/materials",
    title: "Складской срез",
    description: "Остатки, резервы и проблемные позиции по материалам.",
    icon: IconAlertTriangle
  },
  {
    href: "/reports/narad-material-consumption",
    title: "Расход по нарядам",
    description: "Списания материалов по закрытым нарядам и строкам заказов.",
    icon: IconFlask
  },
  {
    href: "/reports/actual-material-consumption",
    title: "Расход по факту",
    description: "Ручные списания материалов без привязки к заказу.",
    icon: IconFlask2
  }
];
