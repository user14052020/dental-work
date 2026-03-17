import { Button, Collapse, Group, Select } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconAdjustmentsHorizontal, IconPrinter, IconTruckDelivery } from "@tabler/icons-react";

import { Client } from "@/entities/clients/model/types";
import { Executor } from "@/entities/executors/model/types";
import { SearchField } from "@/shared/ui/search-field";

type DeliveryToolbarProps = {
  search: string;
  clientId: string;
  executorId: string;
  sentFilter: string;
  clients: Client[];
  executors: Executor[];
  selectedCount: number;
  markSentLoading: boolean;
  onSearchChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onExecutorChange: (value: string) => void;
  onSentFilterChange: (value: string) => void;
  onPrint: () => void;
  onMarkSent: () => void;
};

type DeliveryFilterFieldsProps = {
  className?: string;
  clients: Client[];
  executors: Executor[];
  clientId: string;
  executorId: string;
  sentFilter: string;
  onClientChange: (value: string) => void;
  onExecutorChange: (value: string) => void;
  onSentFilterChange: (value: string) => void;
};

function DeliveryFilterFields({
  className,
  clients,
  executors,
  clientId,
  executorId,
  sentFilter,
  onClientChange,
  onExecutorChange,
  onSentFilterChange
}: DeliveryFilterFieldsProps) {
  return (
    <div className={className}>
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
      <Select
        className="w-full"
        data={[
          { value: "pending", label: "Не отправлены" },
          { value: "sent", label: "Отправлены" },
          { value: "all", label: "Все" }
        ]}
        label="Состояние доставки"
        value={sentFilter}
        onChange={(value) => onSentFilterChange(value ?? "pending")}
      />
    </div>
  );
}

export function DeliveryToolbar({
  search,
  clientId,
  executorId,
  sentFilter,
  clients,
  executors,
  selectedCount,
  markSentLoading,
  onSearchChange,
  onClientChange,
  onExecutorChange,
  onSentFilterChange,
  onPrint,
  onMarkSent
}: DeliveryToolbarProps) {
  const [filtersOpened, { toggle }] = useDisclosure(false);

  return (
    <div className="flex w-full min-w-0 flex-col gap-3">
      <div className="grid w-full gap-3 md:grid-cols-[minmax(0,1.5fr)_repeat(3,minmax(0,1fr))]">
        <SearchField
          className="w-full"
          label="Поиск"
          placeholder="Поиск по заказу, клиенту, врачу, пациенту и адресу доставки"
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
        />
        <div className="hidden md:contents">
          <DeliveryFilterFields
            className="contents"
            clients={clients}
            executors={executors}
            clientId={clientId}
            executorId={executorId}
            sentFilter={sentFilter}
            onClientChange={onClientChange}
            onExecutorChange={onExecutorChange}
            onSentFilterChange={onSentFilterChange}
          />
        </div>
      </div>

      <div className="grid w-full gap-3 md:hidden">
        <Button
          fullWidth
          variant="light"
          color="gray"
          leftSection={<IconAdjustmentsHorizontal size={16} />}
          onClick={toggle}
        >
          {filtersOpened ? "Скрыть фильтры" : "Показать фильтры"}
        </Button>
        <Collapse in={filtersOpened}>
          <DeliveryFilterFields
            className="grid gap-3 pt-3"
            clients={clients}
            executors={executors}
            clientId={clientId}
            executorId={executorId}
            sentFilter={sentFilter}
            onClientChange={onClientChange}
            onExecutorChange={onExecutorChange}
            onSentFilterChange={onSentFilterChange}
          />
        </Collapse>
      </div>

      <Group align="stretch" justify="space-between" wrap="wrap" className="w-full flex-col md:flex-row">
        <div className="text-sm text-slate-500">
          {selectedCount ? `Выбрано заказов: ${selectedCount}` : "Выбери один или несколько заказов для листа доставки."}
        </div>
        <div className="grid w-full gap-3 md:w-auto md:grid-flow-col">
          <Button
            fullWidth
            variant="light"
            leftSection={<IconPrinter size={16} />}
            disabled={!selectedCount}
            onClick={onPrint}
          >
            Печать листа доставки
          </Button>
          <Button
            fullWidth
            leftSection={<IconTruckDelivery size={16} />}
            disabled={!selectedCount}
            loading={markSentLoading}
            onClick={onMarkSent}
          >
            Отметить отправку
          </Button>
        </div>
      </Group>
    </div>
  );
}
