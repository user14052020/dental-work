"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { Narad, NaradCompact } from "@/entities/narads/model/types";
import { useNaradsQuery } from "@/entities/narads/model/use-narads-query";

function toIsoDate(value: string) {
  return value ? new Date(value).toISOString() : undefined;
}

function getInitialQueryValue(key: string) {
  if (typeof window === "undefined") {
    return "";
  }

  return new URLSearchParams(window.location.search).get(key) ?? "";
}

export function useNaradsPage() {
  const [search, setSearch] = useState(() => getInitialQueryValue("search"));
  const [status, setStatus] = useState(() => getInitialQueryValue("status"));
  const [clientId, setClientId] = useState(() => getInitialQueryValue("client_id"));
  const [dateFrom, setDateFrom] = useState(() => getInitialQueryValue("date_from"));
  const [dateTo, setDateTo] = useState(() => getInitialQueryValue("date_to"));
  const [page, setPage] = useState(1);
  const [selectedNarad, setSelectedNarad] = useState<NaradCompact | null>(null);
  const [editingNarad, setEditingNarad] = useState<Narad | null>(null);
  const [workNarad, setWorkNarad] = useState<Narad | null>(null);
  const [lifecycleNarad, setLifecycleNarad] = useState<NaradCompact | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<"close" | "reopen">("close");
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [naradFormOpened, naradFormHandlers] = useDisclosure(false);
  const [workFormOpened, workFormHandlers] = useDisclosure(false);
  const [lifecycleOpened, lifecycleHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [clientId, dateFrom, dateTo, debouncedSearch, status]);

  const naradsQuery = useNaradsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    status: status || undefined,
    client_id: clientId || undefined,
    date_from: toIsoDate(dateFrom),
    date_to: toIsoDate(dateTo)
  });
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });

  return {
    clientId,
    clientsQuery,
    dateFrom,
    dateTo,
    detailOpened,
    editingNarad,
    naradsQuery,
    naradFormOpened,
    page,
    search,
    selectedNarad,
    lifecycleMode,
    lifecycleNarad,
    lifecycleOpened,
    setClientId,
    setDateFrom,
    setDateTo,
    setPage,
    setSearch,
    setStatus,
    status,
    workFormOpened,
    workNarad,
    openView(narad: NaradCompact) {
      setSelectedNarad(narad);
      detailHandlers.open();
    },
    openCreateNarad() {
      setEditingNarad(null);
      naradFormHandlers.open();
    },
    openEditNarad(narad: Narad) {
      setEditingNarad(narad);
      naradFormHandlers.open();
    },
    openCreateWork(narad: Narad) {
      setWorkNarad(narad);
      workFormHandlers.open();
    },
    openCloseLifecycle(narad: NaradCompact) {
      setLifecycleMode("close");
      setLifecycleNarad(narad);
      lifecycleHandlers.open();
    },
    openReopenLifecycle(narad: NaradCompact) {
      setLifecycleMode("reopen");
      setLifecycleNarad(narad);
      lifecycleHandlers.open();
    },
    closeDetail() {
      setSelectedNarad(null);
      detailHandlers.close();
    },
    closeNaradForm() {
      setEditingNarad(null);
      naradFormHandlers.close();
    },
    closeCreateWork() {
      setWorkNarad(null);
      workFormHandlers.close();
    },
    closeLifecycle() {
      setLifecycleNarad(null);
      lifecycleHandlers.close();
    }
  };
}
