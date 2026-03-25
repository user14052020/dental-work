import {
  IconAlertTriangle,
  IconActivityHeartbeat,
  IconBook2,
  IconBriefcase,
  IconBuildingBank,
  IconCalculator,
  IconChecklist,
  IconFlask,
  IconClipboardText,
  IconDashboard,
  IconFlask2,
  IconFiles,
  IconClipboardList,
  IconPackageImport,
  IconCreditCard,
  IconReceipt2,
  IconTopologyStar3,
  IconReportAnalytics,
  IconSettings,
  IconStack2,
  IconStethoscope,
  IconTruckDelivery,
  IconUsers
} from "@tabler/icons-react";

export type NavigationItem = {
  href: string;
  label: string;
  description: string;
  icon: typeof IconDashboard;
  requiredPermissions?: string[];
};

export type HeaderNavigationMenu = {
  label: string;
  icon: typeof IconDashboard;
  items: NavigationItem[];
};

export const sidebarNavigationItems: NavigationItem[] = [
  {
    href: "/dashboard",
    label: "Сводка",
    description: "Метрики, прибыль и быстрые действия",
    icon: IconDashboard,
    requiredPermissions: ["dashboard.view"]
  },
  {
    href: "/narads",
    label: "Наряды",
    description: "Шапки заказов, история статусов и состав работ",
    icon: IconFiles,
    requiredPermissions: ["narads.manage"]
  },
  {
    href: "/works",
    label: "Работы",
    description: "Заказы, статусы и себестоимость",
    icon: IconBriefcase,
    requiredPermissions: ["works.manage"]
  },
  {
    href: "/delivery",
    label: "Доставка",
    description: "Готовые к отправке работы и лист курьера",
    icon: IconTruckDelivery,
    requiredPermissions: ["delivery.manage"]
  },
  {
    href: "/outside-works",
    label: "Работы на стороне",
    description: "Наряды у подрядчиков, сроки возврата и внешняя себестоимость",
    icon: IconTopologyStar3,
    requiredPermissions: ["outside_works.manage"]
  },
  {
    href: "/cost-calculation",
    label: "Себестоимость",
    description: "Калькулятор себестоимости в реальном времени",
    icon: IconCalculator,
    requiredPermissions: ["cost_calculation.view"]
  }
];

export const headerNavigationMenus: HeaderNavigationMenu[] = [
  {
    label: "Клиенты",
    icon: IconUsers,
    items: [
      {
        href: "/clients",
        label: "Клиенты",
        description: "Клиники, суммы заказов и история",
        icon: IconUsers,
        requiredPermissions: ["clients.manage"]
      },
      {
        href: "/payments",
        label: "Платежи",
        description: "Поступления, распределение по заказам и остатки",
        icon: IconCreditCard,
        requiredPermissions: ["payments.manage"]
      }
    ]
  },
  {
    label: "Отчеты",
    icon: IconReportAnalytics,
    items: [
      {
        href: "/reports",
        label: "Каталог отчетов",
        description: "Все отчеты и быстрый вход в аналитику.",
        icon: IconReportAnalytics,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/client-balances",
        label: "Баланс клиентов",
        description: "Задолженность, объем заказов и активность.",
        icon: IconReceipt2,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/narads",
        label: "Реестр нарядов",
        description: "Финансовый и производственный срез по нарядам.",
        icon: IconFiles,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/executors",
        label: "Исполнители",
        description: "Загрузка, закрытые работы и начисления.",
        icon: IconUsers,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/payroll",
        label: "Оплата труда",
        description: "Начисления техникам по закрытым нарядам.",
        icon: IconStack2,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/payroll-operations",
        label: "Операции по нарядам",
        description: "Детализация начислений по операциям.",
        icon: IconClipboardList,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/materials",
        label: "Складской срез",
        description: "Остатки, резервы и проблемные позиции.",
        icon: IconAlertTriangle,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/narad-material-consumption",
        label: "Расход по нарядам",
        description: "Списания материалов по закрытым нарядам.",
        icon: IconFlask,
        requiredPermissions: ["reports.view"]
      },
      {
        href: "/reports/actual-material-consumption",
        label: "Расход по факту",
        description: "Ручные списания материалов без привязки к заказу.",
        icon: IconFlask2,
        requiredPermissions: ["reports.view"]
      }
    ]
  },
  {
    label: "Склад",
    icon: IconFlask2,
    items: [
      {
        href: "/materials",
        label: "Материалы",
        description: "Склад, остатки и списания",
        icon: IconFlask2,
        requiredPermissions: ["materials.manage"]
      },
      {
        href: "/receipts",
        label: "Приходы",
        description: "Поступление материалов и пересчет складской стоимости",
        icon: IconPackageImport,
        requiredPermissions: ["receipts.manage"]
      },
      {
        href: "/inventory-adjustments",
        label: "Инвентаризация",
        description: "Документы пересчета склада и корректировок остатков",
        icon: IconClipboardList,
        requiredPermissions: ["inventory.manage"]
      }
    ]
  },
  {
    label: "Справочники",
    icon: IconBook2,
    items: [
      {
        href: "/executors",
        label: "Исполнители",
        description: "Исполнители, ставки и загрузка",
        icon: IconActivityHeartbeat,
        requiredPermissions: ["executors.manage"]
      },
      {
        href: "/doctors",
        label: "Врачи",
        description: "Справочник врачей клиник и их контактов",
        icon: IconStethoscope,
        requiredPermissions: ["doctors.manage"]
      },
      {
        href: "/contractors",
        label: "Подрядчики",
        description: "Справочник внешних лабораторий и подрядчиков",
        icon: IconTopologyStar3,
        requiredPermissions: ["contractors.manage"]
      },
      {
        href: "/operations",
        label: "Операции",
        description: "Каталог операций и тарифов по категориям",
        icon: IconChecklist,
        requiredPermissions: ["operations.manage"]
      },
      {
        href: "/work-catalog",
        label: "Каталог работ",
        description: "Шаблоны работ, базовые цены и операции",
        icon: IconClipboardText,
        requiredPermissions: ["work_catalog.manage"]
      }
    ]
  },
  {
    label: "Настройки",
    icon: IconSettings,
    items: [
      {
        href: "/employees",
        label: "Сотрудники",
        description: "Сотрудники, техники и права доступа",
        icon: IconUsers,
        requiredPermissions: ["employees.manage"]
      },
      {
        href: "/organization",
        label: "Организация",
        description: "Реквизиты лаборатории и печатные документы",
        icon: IconBuildingBank,
        requiredPermissions: ["organization.manage"]
      }
    ]
  }
];
