"use client";

import { useDisclosure, useDebouncedValue } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Employee } from "@/entities/employees/model/types";
import { useEmployeesQuery } from "@/entities/employees/model/use-employees-query";

export function useEmployeesPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [includeFired, setIncludeFired] = useState(false);
  const [editedEmployee, setEditedEmployee] = useState<Employee | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, includeFired]);

  const employeesQuery = useEmployeesQuery({
    page,
    page_size: 12,
    search: debouncedSearch || undefined,
    include_fired: includeFired
  });

  return {
    employeesQuery,
    editedEmployee,
    formOpened,
    includeFired,
    page,
    search,
    setIncludeFired,
    setPage,
    setSearch,
    openCreate() {
      setEditedEmployee(null);
      formHandlers.open();
    },
    openEdit(employee: Employee) {
      setEditedEmployee(employee);
      formHandlers.open();
    },
    closeForm() {
      setEditedEmployee(null);
      formHandlers.close();
    }
  };
}
