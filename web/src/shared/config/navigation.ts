import {
  IconActivityHeartbeat,
  IconBriefcase,
  IconCalculator,
  IconDashboard,
  IconFlask2,
  IconUsers
} from "@tabler/icons-react";

export type NavigationItem = {
  href: string;
  label: string;
  description: string;
  icon: typeof IconDashboard;
};

export const navigationItems: NavigationItem[] = [
  {
    href: "/dashboard",
    label: "Сводка",
    description: "Метрики, прибыль и быстрые действия",
    icon: IconDashboard
  },
  {
    href: "/clients",
    label: "Клиенты",
    description: "Клиники, суммы заказов и история",
    icon: IconUsers
  },
  {
    href: "/executors",
    label: "Исполнители",
    description: "Исполнители, ставки и загрузка",
    icon: IconActivityHeartbeat
  },
  {
    href: "/materials",
    label: "Материалы",
    description: "Склад, остатки и списания",
    icon: IconFlask2
  },
  {
    href: "/works",
    label: "Работы",
    description: "Заказы, статусы и себестоимость",
    icon: IconBriefcase
  },
  {
    href: "/cost-calculation",
    label: "Себестоимость",
    description: "Калькулятор себестоимости в реальном времени",
    icon: IconCalculator
  }
];
