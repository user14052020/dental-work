export type EmployeePermissionDefinition = {
  code: string;
  label: string;
  description: string;
};

export type EmployeePermissionGroup = {
  key: string;
  label: string;
  items: EmployeePermissionDefinition[];
};

export const employeePermissionGroups: EmployeePermissionGroup[] = [
  {
    key: "overview",
    label: "Обзор и расчеты",
    items: [
      { code: "dashboard.view", label: "Сводка", description: "Главный дашборд лаборатории и ключевые метрики." },
      {
        code: "cost_calculation.view",
        label: "Себестоимость",
        description: "Расчет себестоимости работ, операций и материалов."
      }
    ]
  },
  {
    key: "catalogs",
    label: "Справочники",
    items: [
      { code: "clients.manage", label: "Заказчики", description: "Карточки заказчиков и их реквизиты." },
      { code: "contractors.manage", label: "Подрядчики", description: "Внешние лаборатории и подрядчики." },
      { code: "doctors.manage", label: "Врачи", description: "Справочник врачей и их контакты." },
      { code: "executors.manage", label: "Исполнители", description: "Техники, ставки и категории оплаты." },
      { code: "materials.manage", label: "Материалы", description: "Складские позиции и лимиты." },
      { code: "operations.manage", label: "Операции", description: "Операции и тарифы по категориям." },
      { code: "work_catalog.manage", label: "Каталог работ", description: "Шаблоны работ и их операции." }
    ]
  },
  {
    key: "production",
    label: "Производство",
    items: [
      { code: "narads.manage", label: "Наряды", description: "Создание, редактирование и закрытие нарядов." },
      { code: "works.manage", label: "Работы", description: "Создание и ведение работ внутри нарядов." },
      { code: "delivery.manage", label: "Доставка", description: "Работа с доставкой и путевыми листами." },
      {
        code: "outside_works.manage",
        label: "Работы на стороне",
        description: "Отправка нарядов подрядчикам и возврат из внешнего производства."
      },
      { code: "receipts.manage", label: "Приходы", description: "Оформление приходов и складских движений." },
      {
        code: "inventory.manage",
        label: "Инвентаризация",
        description: "Документы пересчета склада и корректировок остатков."
      }
    ]
  },
  {
    key: "finance",
    label: "Финансы",
    items: [
      { code: "payments.manage", label: "Платежи", description: "Поступления и распределение оплат." },
      { code: "reports.view", label: "Отчеты", description: "Доступ к аналитике, зарплате и складским отчетам." },
      { code: "organization.manage", label: "Организация", description: "Реквизиты, НДС и печатные настройки." }
    ]
  },
  {
    key: "settings",
    label: "Настройки доступа",
    items: [
      { code: "employees.manage", label: "Сотрудники", description: "Создание, изменение и увольнение сотрудников." },
      { code: "permissions.manage", label: "Права", description: "Назначение прав доступа сотрудникам." }
    ]
  }
];
