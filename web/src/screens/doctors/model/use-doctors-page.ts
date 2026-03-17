"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Doctor } from "@/entities/doctors/model/types";
import { useDoctorsQuery } from "@/entities/doctors/model/use-doctors-query";

export function useDoctorsPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [editedDoctor, setEditedDoctor] = useState<Doctor | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [activeOnly, debouncedSearch]);

  const doctorsQuery = useDoctorsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    active_only: activeOnly || undefined
  });

  return {
    activeOnly,
    doctorsQuery,
    editedDoctor,
    formOpened,
    page,
    search,
    setActiveOnly,
    setPage,
    setSearch,
    openCreate() {
      setEditedDoctor(null);
      formHandlers.open();
    },
    openEdit(doctor: Doctor) {
      setEditedDoctor(doctor);
      formHandlers.open();
    },
    closeForm() {
      setEditedDoctor(null);
      formHandlers.close();
    }
  };
}
