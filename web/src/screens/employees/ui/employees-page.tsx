"use client";

import { EmployeeFormModal } from "@/features/employees/upsert-employee/ui/employee-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { EmployeesTable } from "@/widgets/employees-panel/ui/employees-table";
import { EmployeesToolbar } from "@/widgets/employees-panel/ui/employees-toolbar";

import { useEmployeesPage } from "../model/use-employees-page";

export function EmployeesPage() {
  const page = useEmployeesPage();

  return (
    <>
      <PageHeading
        title="Сотрудники"
        description="Сотрудники лаборатории, учет техников и назначение прав доступа к разделам программы."
      >
        <EmployeesToolbar
          search={page.search}
          includeFired={page.includeFired}
          onSearchChange={page.setSearch}
          onIncludeFiredChange={page.setIncludeFired}
          onCreate={page.openCreate}
        />
        <EmployeesTable
          items={page.employeesQuery.data?.items ?? []}
          meta={page.employeesQuery.data?.meta}
          isLoading={page.employeesQuery.isLoading}
          onPageChange={page.setPage}
          onEdit={page.openEdit}
        />
      </PageHeading>

      <EmployeeFormModal employee={page.editedEmployee} opened={page.formOpened} onClose={page.closeForm} />
    </>
  );
}
