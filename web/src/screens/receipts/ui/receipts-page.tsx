"use client";

import { ReceiptDetailDrawer } from "@/features/receipts/view-receipt/ui/receipt-detail-drawer";
import { ReceiptFormModal } from "@/features/receipts/upsert-receipt/ui/receipt-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { ReceiptsTable } from "@/widgets/receipts-panel/ui/receipts-table";
import { ReceiptsToolbar } from "@/widgets/receipts-panel/ui/receipts-toolbar";

import { useReceiptsPage } from "../model/use-receipts-page";

export function ReceiptsPage() {
  const page = useReceiptsPage();

  return (
    <>
      <PageHeading
        title="Приходы"
        description="Документы поступления материалов на склад с пересчётом остатков, средней цены и полной историей движения."
      >
        <ReceiptsToolbar
          search={page.search}
          supplier={page.supplier}
          dateFrom={page.dateFrom}
          dateTo={page.dateTo}
          onSearchChange={page.setSearch}
          onSupplierChange={page.setSupplier}
          onDateFromChange={page.setDateFrom}
          onDateToChange={page.setDateTo}
          onCreate={page.openCreate}
        />
        <ReceiptsTable
          items={page.receiptsQuery.data?.items ?? []}
          meta={page.receiptsQuery.data?.meta}
          isLoading={page.receiptsQuery.isLoading}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <ReceiptFormModal opened={page.formOpened} onClose={page.closeCreate} />
      <ReceiptDetailDrawer receiptId={page.selectedReceipt?.id} opened={page.detailOpened} onClose={page.closeDetail} />
    </>
  );
}
