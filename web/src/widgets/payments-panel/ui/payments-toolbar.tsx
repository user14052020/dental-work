import { Button, Select, TextInput } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { paymentMethodOptions, PaymentMethod } from "@/entities/payments/model/types";
import { SearchField } from "@/shared/ui/search-field";

type PaymentsToolbarProps = {
  search: string;
  clientId: string;
  clients: Client[];
  method: PaymentMethod | "";
  dateFrom: string;
  dateTo: string;
  onSearchChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onMethodChange: (value: PaymentMethod | "") => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onCreate: () => void;
};

export function PaymentsToolbar({
  search,
  clientId,
  clients,
  method,
  dateFrom,
  dateTo,
  onSearchChange,
  onClientChange,
  onMethodChange,
  onDateFromChange,
  onDateToChange,
  onCreate
}: PaymentsToolbarProps) {
  const clientOptions = clients.map((client) => ({
    value: client.id,
    label: client.name
  }));

  return (
    <div className="flex min-w-0 w-full flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div className="grid w-full gap-3 md:flex-1 md:grid-cols-2 xl:grid-cols-5">
        <SearchField
          className="w-full xl:col-span-2"
          label="Поиск"
          placeholder="Поиск по номеру платежа, клиенту, заказу или комментарию"
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
        />
        <Select
          clearable
          data={clientOptions}
          label="Клиент"
          placeholder="Все клиенты"
          value={clientId || null}
          onChange={(value) => onClientChange(value ?? "")}
        />
        <Select
          clearable
          data={paymentMethodOptions}
          label="Способ оплаты"
          placeholder="Любой"
          value={method || null}
          onChange={(value) => onMethodChange((value as PaymentMethod | null) ?? "")}
        />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-2">
          <TextInput
            label="С даты"
            type="date"
            value={dateFrom}
            onChange={(event) => onDateFromChange(event.currentTarget.value)}
          />
          <TextInput
            label="По дату"
            type="date"
            value={dateTo}
            onChange={(event) => onDateToChange(event.currentTarget.value)}
          />
        </div>
      </div>
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto md:self-end">
        Новый платеж
      </Button>
    </div>
  );
}
