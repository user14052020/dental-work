"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { OutsideWorkItem } from "@/entities/narads/model/types";
import { useOutsideWorksQuery } from "@/entities/narads/model/use-narads-query";

export function useOutsideWorksPage() {
  const [search, setSearch] = useState("");
  const [clientId, setClientId] = useState("");
  const [state, setState] = useState("all");
  const [page, setPage] = useState(1);
  const [selectedNaradId, setSelectedNaradId] = useState<string>();
  const [selectedItem, setSelectedItem] = useState<OutsideWorkItem | null>(null);
  const [mode, setMode] = useState<"sent" | "returned">("sent");
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [modalOpened, modalHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [clientId, debouncedSearch, state]);

  const outsideWorksQuery = useOutsideWorksQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    client_id: clientId || undefined,
    state: state === "all" ? undefined : state
  });
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });

  return {
    clientId,
    clientsQuery,
    detailOpened,
    modalOpened,
    mode,
    outsideWorksQuery,
    page,
    search,
    selectedItem,
    selectedNaradId,
    state,
    setClientId,
    setPage,
    setSearch,
    setState,
    closeDetail() {
      setSelectedNaradId(undefined);
      detailHandlers.close();
    },
    closeModal() {
      setSelectedItem(null);
      modalHandlers.close();
    },
    openView(naradId: string) {
      setSelectedNaradId(naradId);
      detailHandlers.open();
    },
    openMarkSent(item: OutsideWorkItem) {
      setMode("sent");
      setSelectedItem(item);
      modalHandlers.open();
    },
    openMarkReturned(item: OutsideWorkItem) {
      setMode("returned");
      setSelectedItem(item);
      modalHandlers.open();
    }
  };
}
