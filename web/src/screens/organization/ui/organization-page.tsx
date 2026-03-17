"use client";

import { OrganizationProfileForm } from "@/features/organization/upsert-profile/ui/organization-profile-form";
import { PageHeading } from "@/shared/ui/page-heading";

export function OrganizationPage() {
  return (
    <PageHeading
      title="Организация"
      description="Текущие реквизиты лаборатории для счетов, актов и печатного наряда."
    >
      <OrganizationProfileForm />
    </PageHeading>
  );
}
