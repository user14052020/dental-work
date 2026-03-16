"use client";

import { useDisclosure, useDebouncedValue } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Client } from "@/entities/clients/model/types";
import { useClientsQuery } from "@/entities/clients/model/use-clients-query";

export function useClientsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [editedClient, setEditedClient] = useState<Client | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch]);

  const clientsQuery = useClientsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined
  });

  return {
    clientsQuery,
    detailOpened,
    editedClient,
    formOpened,
    page,
    search,
    selectedClient,
    setPage,
    setSearch,
    openCreate() {
      setEditedClient(null);
      formHandlers.open();
    },
    openEdit(client: Client) {
      setEditedClient(client);
      formHandlers.open();
    },
    openView(client: Client) {
      setSelectedClient(client);
      detailHandlers.open();
    },
    closeForm() {
      setEditedClient(null);
      formHandlers.close();
    },
    closeDetail() {
      setSelectedClient(null);
      detailHandlers.close();
    }
  };
}
