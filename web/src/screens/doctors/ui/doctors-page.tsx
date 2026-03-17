"use client";

import { DoctorFormModal } from "@/features/doctors/upsert-doctor/ui/doctor-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { DoctorsTable } from "@/widgets/doctors-panel/ui/doctors-table";
import { DoctorsToolbar } from "@/widgets/doctors-panel/ui/doctors-toolbar";

import { useDoctorsPage } from "../model/use-doctors-page";

export function DoctorsPage() {
  const page = useDoctorsPage();

  return (
    <>
      <PageHeading
        title="Врачи"
        description="Справочник врачей клиник-заказчиков. Используется в работах, печатных формах и последующей аналитике по нарядам."
      >
        <DoctorsToolbar
          activeOnly={page.activeOnly}
          onActiveOnlyChange={page.setActiveOnly}
          onCreate={page.openCreate}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <DoctorsTable
          isLoading={page.doctorsQuery.isLoading}
          items={page.doctorsQuery.data?.items ?? []}
          meta={page.doctorsQuery.data?.meta}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
        />
      </PageHeading>

      <DoctorFormModal
        doctor={page.editedDoctor}
        opened={page.formOpened}
        onClose={page.closeForm}
      />
    </>
  );
}
