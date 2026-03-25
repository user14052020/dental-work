"use client";

import { useDisclosure, useDebouncedValue } from "@mantine/hooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { deletePayment } from "@/entities/payments/api/payments-api";
import { PaymentCompact, PaymentMethod } from "@/entities/payments/model/types";
import { paymentsQueryKeys } from "@/entities/payments/model/query-keys";
import { usePaymentsQuery } from "@/entities/payments/model/use-payments-query";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

function toIsoStart(value: string) {
  return value ? new Date(`${value}T00:00:00`).toISOString() : undefined;
}

function toIsoEnd(value: string) {
  return value ? new Date(`${value}T23:59:59`).toISOString() : undefined;
}

export function usePaymentsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [clientId, setClientId] = useState("");
  const [method, setMethod] = useState<PaymentMethod | "">("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [editedPayment, setEditedPayment] = useState<PaymentCompact | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [clientId, dateFrom, dateTo, debouncedSearch, method]);

  const paymentsQuery = usePaymentsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    client_id: clientId || undefined,
    method: method || undefined,
    date_from: toIsoStart(dateFrom),
    date_to: toIsoEnd(dateTo)
  });
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });

  const deleteMutation = useMutation({
    mutationFn: (paymentId: string) => deletePayment(paymentId),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: paymentsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Платеж удален.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось удалить платеж.");
    }
  });

  return {
    clientId,
    clientsQuery,
    dateFrom,
    dateTo,
    editedPayment,
    formOpened,
    method,
    page,
    paymentsQuery,
    search,
    setClientId,
    setDateFrom,
    setDateTo,
    setMethod,
    setPage,
    setSearch,
    openCreate() {
      setEditedPayment(null);
      formHandlers.open();
    },
    openEdit(payment: PaymentCompact) {
      setEditedPayment(payment);
      formHandlers.open();
    },
    closeForm() {
      setEditedPayment(null);
      formHandlers.close();
    },
    deletePayment(payment: PaymentCompact) {
      if (!window.confirm(`Удалить платеж ${payment.payment_number}?`)) {
        return;
      }
      deleteMutation.mutate(payment.id);
    }
  };
}
