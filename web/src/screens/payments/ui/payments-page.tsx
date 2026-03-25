"use client";

import { PaymentFormModal } from "@/features/payments/upsert-payment/ui/payment-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { PaymentsTable } from "@/widgets/payments-panel/ui/payments-table";
import { PaymentsToolbar } from "@/widgets/payments-panel/ui/payments-toolbar";

import { usePaymentsPage } from "../model/use-payments-page";

export function PaymentsPage() {
  const page = usePaymentsPage();

  return (
    <>
      <PageHeading
        title="Платежи"
        description="Реестр поступлений с распределением одной оплаты на несколько заказов и контролем нераспределенного остатка."
      >
        <PaymentsToolbar
          search={page.search}
          clientId={page.clientId}
          clients={page.clientsQuery.data?.items ?? []}
          method={page.method}
          dateFrom={page.dateFrom}
          dateTo={page.dateTo}
          onSearchChange={page.setSearch}
          onClientChange={page.setClientId}
          onMethodChange={page.setMethod}
          onDateFromChange={page.setDateFrom}
          onDateToChange={page.setDateTo}
          onCreate={page.openCreate}
        />
        <PaymentsTable
          isLoading={page.paymentsQuery.isLoading}
          items={page.paymentsQuery.data?.items ?? []}
          meta={page.paymentsQuery.data?.meta}
          onPageChange={page.setPage}
          onEdit={page.openEdit}
          onDelete={page.deletePayment}
        />
      </PageHeading>

      <PaymentFormModal payment={page.editedPayment} opened={page.formOpened} onClose={page.closeForm} />
    </>
  );
}
