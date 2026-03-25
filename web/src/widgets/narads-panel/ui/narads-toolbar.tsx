import { Button, Group, Select, TextInput } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { workStatusOptions } from "@/entities/works/model/types";
import { SearchField } from "@/shared/ui/search-field";

type NaradsToolbarProps = {
  search: string;
  status: string;
  clientId: string;
  dateFrom: string;
  dateTo: string;
  clients: Client[];
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onCreate: () => void;
};

export function NaradsToolbar({
  search,
  status,
  clientId,
  dateFrom,
  dateTo,
  clients,
  onSearchChange,
  onStatusChange,
  onClientChange,
  onDateFromChange,
  onDateToChange,
  onCreate
}: NaradsToolbarProps) {
  const statusOptions = [
    { value: "overdue", label: "Просроченные" },
    ...workStatusOptions.map((item) => ({ value: item.value, label: item.label }))
  ];

  return (
    <Group align="end" wrap="wrap" className="w-full">
      <SearchField
        className="w-full md:flex-1"
        label="Поиск"
        placeholder="Поиск по номеру наряда, клиенту, врачу и пациенту"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Select
        clearable
        className="w-full md:max-w-[220px]"
        data={statusOptions}
        label="Статус"
        value={status || null}
        onChange={(value) => onStatusChange(value ?? "")}
      />
      <Select
        clearable
        className="w-full md:max-w-[260px]"
        data={clients.map((client) => ({ value: client.id, label: client.name }))}
        label="Клиент"
        value={clientId || null}
        onChange={(value) => onClientChange(value ?? "")}
      />
      <TextInput
        className="w-full md:max-w-[180px]"
        label="С даты"
        type="date"
        value={dateFrom}
        onChange={(event) => onDateFromChange(event.currentTarget.value)}
      />
      <TextInput
        className="w-full md:max-w-[180px]"
        label="По дату"
        type="date"
        value={dateTo}
        onChange={(event) => onDateToChange(event.currentTarget.value)}
      />
      <Button className="w-full md:w-auto" leftSection={<IconPlus size={16} />} onClick={onCreate}>
        Новый наряд
      </Button>
    </Group>
  );
}
