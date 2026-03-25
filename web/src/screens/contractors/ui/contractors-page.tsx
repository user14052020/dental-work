"use client";

import { ContractorFormModal } from "@/features/contractors/upsert-contractor/ui/contractor-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { ContractorsTable } from "@/widgets/contractors-panel/ui/contractors-table";
import { ContractorsToolbar } from "@/widgets/contractors-panel/ui/contractors-toolbar";

import { useContractorsPage } from "../model/use-contractors-page";

export function ContractorsPage() {
  const page = useContractorsPage();

  return (
    <>
      <PageHeading
        title="Подрядчики"
        description="Справочник внешних лабораторий и подрядчиков. Используется в работах на стороне и нарядах внешнего производства."
      >
        <ContractorsToolbar
          activeOnly={page.activeOnly}
          onActiveOnlyChange={page.setActiveOnly}
          onCreate={page.openCreate}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <ContractorsTable
          isLoading={page.contractorsQuery.isLoading}
          items={page.contractorsQuery.data?.items ?? []}
          meta={page.contractorsQuery.data?.meta}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
        />
      </PageHeading>

      <ContractorFormModal contractor={page.editedContractor} opened={page.formOpened} onClose={page.closeForm} />
    </>
  );
}
