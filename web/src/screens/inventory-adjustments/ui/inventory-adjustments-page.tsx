"use client";

import { InventoryAdjustmentFormModal } from "@/features/inventory-adjustments/upsert-adjustment/ui/inventory-adjustment-form-modal";
import { InventoryAdjustmentDetailDrawer } from "@/features/inventory-adjustments/view-adjustment/ui/inventory-adjustment-detail-drawer";
import { PageHeading } from "@/shared/ui/page-heading";
import { InventoryAdjustmentsTable } from "@/widgets/inventory-adjustments-panel/ui/inventory-adjustments-table";
import { InventoryAdjustmentsToolbar } from "@/widgets/inventory-adjustments-panel/ui/inventory-adjustments-toolbar";

import { useInventoryAdjustmentsPage } from "../model/use-inventory-adjustments-page";

export function InventoryAdjustmentsPage() {
  const page = useInventoryAdjustmentsPage();

  return (
    <>
      <PageHeading
        title="Инвентаризация"
        description="Документы пересчета склада с фиксацией ожидаемого остатка, факта и корректирующих движений."
      >
        <InventoryAdjustmentsToolbar
          search={page.search}
          dateFrom={page.dateFrom}
          dateTo={page.dateTo}
          onSearchChange={page.setSearch}
          onDateFromChange={page.setDateFrom}
          onDateToChange={page.setDateTo}
          onCreate={page.openCreate}
        />
        <InventoryAdjustmentsTable
          items={page.adjustmentsQuery.data?.items ?? []}
          meta={page.adjustmentsQuery.data?.meta}
          isLoading={page.adjustmentsQuery.isLoading}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <InventoryAdjustmentFormModal opened={page.formOpened} onClose={page.closeCreate} />
      <InventoryAdjustmentDetailDrawer
        adjustmentId={page.selectedAdjustment?.id}
        opened={page.detailOpened}
        onClose={page.closeDetail}
      />
    </>
  );
}
