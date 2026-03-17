import {
  IconActivityHeartbeat,
  IconBriefcase,
  IconCalculator,
  IconChecklist,
  IconClipboardText,
  IconDashboard,
  IconFlask2,
  IconBuildingBank,
  IconStethoscope,
  IconTruckDelivery,
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
    href: "/doctors",
    label: "Врачи",
    description: "Справочник врачей клиник и их контактов",
    icon: IconStethoscope
  },
  {
    href: "/materials",
    label: "Материалы",
    description: "Склад, остатки и списания",
    icon: IconFlask2
  },
  {
    href: "/organization",
    label: "Организация",
    description: "Реквизиты лаборатории и печатные документы",
    icon: IconBuildingBank
  },
  {
    href: "/operations",
    label: "Операции",
    description: "Каталог операций и тарифов по категориям",
    icon: IconChecklist
  },
  {
    href: "/work-catalog",
    label: "Каталог работ",
    description: "Шаблоны работ, базовые цены и операции",
    icon: IconClipboardText
  },
  {
    href: "/works",
    label: "Работы",
    description: "Заказы, статусы и себестоимость",
    icon: IconBriefcase
  },
  {
    href: "/delivery",
    label: "Доставка",
    description: "Готовые к отправке работы и лист курьера",
    icon: IconTruckDelivery
  },
  {
    href: "/cost-calculation",
    label: "Себестоимость",
    description: "Калькулятор себестоимости в реальном времени",
    icon: IconCalculator
  }
];
