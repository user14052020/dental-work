import { Button, Collapse, Select, TextInput } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconAdjustmentsHorizontal, IconPlus } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { Executor } from "@/entities/executors/model/types";
import { workStatusOptions } from "@/entities/works/model/types";
import { cn } from "@/shared/lib/cn";
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

type WorksFilterFieldsProps = {
  includeSearch?: boolean;
  className?: string;
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
};

function WorksFilterFields({
  includeSearch = true,
  className,
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
  onDateToChange
}: WorksFilterFieldsProps) {
  return (
    <div className={cn("grid w-full gap-3", className)}>
      {includeSearch ? (
        <SearchField
          className="w-full"
          label="Поиск"
          placeholder="Поиск по номеру, клиенту, исполнителю, операции и описанию"
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
        />
      ) : null}
      <Select
        clearable
        className="w-full"
        data={workStatusOptions.map((item) => ({ value: item.value, label: item.label }))}
        label="Статус"
        value={status || null}
        onChange={(value) => onStatusChange(value ?? "")}
      />
      <Select
        clearable
        className="w-full"
        data={clients.map((client) => ({ value: client.id, label: client.name }))}
        label="Клиент"
        value={clientId || null}
        onChange={(value) => onClientChange(value ?? "")}
      />
      <Select
        clearable
        className="w-full"
        data={executors.map((executor) => ({ value: executor.id, label: executor.full_name }))}
        label="Исполнитель"
        value={executorId || null}
        onChange={(value) => onExecutorChange(value ?? "")}
      />
      <TextInput
        className="w-full"
        label="С даты"
        type="date"
        value={dateFrom}
        onChange={(event) => onDateFromChange(event.currentTarget.value)}
      />
      <TextInput
        className="w-full"
        label="По дату"
        type="date"
        value={dateTo}
        onChange={(event) => onDateToChange(event.currentTarget.value)}
      />
    </div>
  );
}

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
  const [filtersOpened, { toggle }] = useDisclosure(false);

  return (
    <div className="flex min-w-0 w-full flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div className="min-w-0 w-full md:flex-1">
        <WorksFilterFields
          className="hidden md:grid md:grid-cols-3 xl:grid-cols-6"
          search={search}
          status={status}
          clientId={clientId}
          executorId={executorId}
          dateFrom={dateFrom}
          dateTo={dateTo}
          clients={clients}
          executors={executors}
          onSearchChange={onSearchChange}
          onStatusChange={onStatusChange}
          onClientChange={onClientChange}
          onExecutorChange={onExecutorChange}
          onDateFromChange={onDateFromChange}
          onDateToChange={onDateToChange}
        />

        <div className="grid w-full gap-3 md:hidden">
          <SearchField
            className="w-full"
            label="Поиск"
            placeholder="Поиск по номеру, клиенту, исполнителю, операции и описанию"
            value={search}
            onChange={(event) => onSearchChange(event.currentTarget.value)}
          />
          <Button
            fullWidth
            variant="light"
            color="gray"
            leftSection={<IconAdjustmentsHorizontal size={16} />}
            onClick={toggle}
          >
            {filtersOpened ? "Скрыть доп. фильтры" : "Показать доп. фильтры"}
          </Button>
          <Collapse in={filtersOpened} className="w-full">
            <WorksFilterFields
              includeSearch={false}
              className="pt-3"
              search={search}
              status={status}
              clientId={clientId}
              executorId={executorId}
              dateFrom={dateFrom}
              dateTo={dateTo}
              clients={clients}
              executors={executors}
              onSearchChange={onSearchChange}
              onStatusChange={onStatusChange}
              onClientChange={onClientChange}
              onExecutorChange={onExecutorChange}
              onDateFromChange={onDateFromChange}
              onDateToChange={onDateToChange}
            />
          </Collapse>
        </div>
      </div>
      <Button
        leftSection={<IconPlus size={16} />}
        onClick={onCreate}
        className="w-full md:w-auto md:self-end"
      >
        Новая работа
      </Button>
    </div>
  );
}
