"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Contractor } from "@/entities/contractors/model/types";
import { useContractorsQuery } from "@/entities/contractors/model/use-contractors-query";

export function useContractorsPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [editedContractor, setEditedContractor] = useState<Contractor | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [activeOnly, debouncedSearch]);

  const contractorsQuery = useContractorsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    active_only: activeOnly || undefined
  });

  return {
    activeOnly,
    contractorsQuery,
    editedContractor,
    formOpened,
    page,
    search,
    setActiveOnly,
    setPage,
    setSearch,
    openCreate() {
      setEditedContractor(null);
      formHandlers.open();
    },
    openEdit(contractor: Contractor) {
      setEditedContractor(contractor);
      formHandlers.open();
    },
    closeForm() {
      setEditedContractor(null);
      formHandlers.close();
    }
  };
}
