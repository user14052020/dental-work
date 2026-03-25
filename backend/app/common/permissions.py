from __future__ import annotations

from typing import Final


ADMIN_PERMISSION: Final = "*"

PERMISSION_GROUPS: Final = [
    {
        "key": "overview",
        "label": "Обзор и расчеты",
        "items": [
            {"code": "dashboard.view", "label": "Сводка", "description": "Доступ к главному дашборду лаборатории."},
            {
                "code": "cost_calculation.view",
                "label": "Себестоимость",
                "description": "Доступ к расчету себестоимости работ и операций.",
            },
        ],
    },
    {
        "key": "catalogs",
        "label": "Справочники",
        "items": [
            {"code": "clients.manage", "label": "Заказчики", "description": "Управление карточками заказчиков и их реквизитами."},
            {"code": "contractors.manage", "label": "Подрядчики", "description": "Справочник внешних лабораторий и подрядчиков."},
            {"code": "doctors.manage", "label": "Врачи", "description": "Управление справочником врачей и контактами."},
            {"code": "executors.manage", "label": "Исполнители", "description": "Управление техниками, ставками и категориями оплаты."},
            {"code": "materials.manage", "label": "Материалы", "description": "Управление складскими позициями и лимитами материалов."},
            {"code": "operations.manage", "label": "Операции", "description": "Управление каталогом операций и тарифов."},
            {"code": "work_catalog.manage", "label": "Каталог работ", "description": "Управление шаблонами работ и их операциями."},
        ],
    },
    {
        "key": "production",
        "label": "Производство",
        "items": [
            {"code": "narads.manage", "label": "Наряды", "description": "Создание, редактирование и закрытие нарядов."},
            {"code": "works.manage", "label": "Работы", "description": "Создание и ведение работ внутри нарядов."},
            {"code": "delivery.manage", "label": "Доставка", "description": "Работа с доставкой и путевыми листами."},
            {
                "code": "outside_works.manage",
                "label": "Работы на стороне",
                "description": "Отправка нарядов подрядчикам и возврат из внешнего производства.",
            },
            {"code": "receipts.manage", "label": "Приходы", "description": "Оформление приходов и складских движений."},
            {
                "code": "inventory.manage",
                "label": "Инвентаризация",
                "description": "Документы пересчета склада и корректировок остатков.",
            },
        ],
    },
    {
        "key": "finance",
        "label": "Финансы",
        "items": [
            {"code": "payments.manage", "label": "Платежи", "description": "Поступления, распределения и контроль оплат."},
            {"code": "reports.view", "label": "Отчеты", "description": "Доступ к аналитике, зарплате и складским отчетам."},
            {"code": "organization.manage", "label": "Организация", "description": "Реквизиты, НДС и печатные настройки."},
        ],
    },
    {
        "key": "settings",
        "label": "Настройки доступа",
        "items": [
            {
                "code": "employees.manage",
                "label": "Сотрудники",
                "description": "Создание, изменение и увольнение сотрудников.",
            },
            {
                "code": "permissions.manage",
                "label": "Права",
                "description": "Назначение прав доступа сотрудникам.",
            },
        ],
    },
]

VALID_PERMISSION_CODES: Final = {
    item["code"] for group in PERMISSION_GROUPS for item in group["items"]
}

DEFAULT_ADMIN_PERMISSION_CODES: Final = [ADMIN_PERMISSION]


def normalize_permission_codes(permission_codes: list[str] | None) -> list[str]:
    if not permission_codes:
        return []
    normalized = [code.strip() for code in permission_codes if code and code.strip()]
    if ADMIN_PERMISSION in normalized:
        return [ADMIN_PERMISSION]
    return sorted({code for code in normalized if code in VALID_PERMISSION_CODES})


def has_permission(permission_codes: list[str] | None, required_code: str) -> bool:
    normalized = normalize_permission_codes(permission_codes)
    return ADMIN_PERMISSION in normalized or required_code in normalized
