import { Button, Group, Select, TextInput } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { Executor } from "@/entities/executors/model/types";
import { workStatusOptions } from "@/entities/works/model/types";
import { SearchField } from "@/shared/ui/search-field";

type WorksToolbarProps = {
  search: string;
  status: string;
  clientId: string;
  executorId: string;
  dateFrom: string;
  dateTo: string;
  clients: Client[];
  executors: Executor[];
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onExecutorChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onCreate: () => void;
};

export function WorksToolbar({
  search,
  status,
  clientId,
  executorId,
  dateFrom,
  dateTo,
  clients,
  executors,
  onSearchChange,
  onStatusChange,
  onClientChange,
  onExecutorChange,
  onDateFromChange,
  onDateToChange,
  onCreate
}: WorksToolbarProps) {
  return (
    <Group align="end" justify="space-between" wrap="wrap" className="min-w-0">
      <div className="grid min-w-0 flex-1 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <SearchField
          label="Поиск"
          placeholder="Поиск по номеру, клиенту, исполнителю, описанию"
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
        />
        <Select
          clearable
          data={workStatusOptions.map((item) => ({ value: item.value, label: item.label }))}
          label="Статус"
          value={status || null}
          onChange={(value) => onStatusChange(value ?? "")}
        />
        <Select
          clearable
          data={clients.map((client) => ({ value: client.id, label: client.name }))}
          label="Клиент"
          value={clientId || null}
          onChange={(value) => onClientChange(value ?? "")}
        />
        <Select
          clearable
          data={executors.map((executor) => ({ value: executor.id, label: executor.full_name }))}
          label="Исполнитель"
          value={executorId || null}
          onChange={(value) => onExecutorChange(value ?? "")}
        />
        <TextInput label="С даты" type="date" value={dateFrom} onChange={(event) => onDateFromChange(event.currentTarget.value)} />
        <TextInput label="По дату" type="date" value={dateTo} onChange={(event) => onDateToChange(event.currentTarget.value)} />
      </div>
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate}>
        Новая работа
      </Button>
    </Group>
  );
}
