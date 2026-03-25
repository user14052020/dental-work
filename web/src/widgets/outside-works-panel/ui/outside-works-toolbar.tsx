import { Group, Select } from "@mantine/core";

import { Client } from "@/entities/clients/model/types";
import { SearchField } from "@/shared/ui/search-field";

type OutsideWorksToolbarProps = {
  search: string;
  clientId: string;
  state: string;
  clients: Client[];
  onSearchChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onStateChange: (value: string) => void;
};

export function OutsideWorksToolbar({
  search,
  clientId,
  state,
  clients,
  onSearchChange,
  onClientChange,
  onStateChange
}: OutsideWorksToolbarProps) {
  return (
    <Group align="end" wrap="wrap" className="w-full">
      <SearchField
        className="w-full md:flex-1"
        label="Поиск"
        placeholder="Поиск по наряду, клиенту, пациенту, подрядчику и внешнему номеру"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Select
        clearable
        className="w-full md:max-w-[260px]"
        data={clients.map((client) => ({ value: client.id, label: client.name }))}
        label="Клиент"
        value={clientId || null}
        onChange={(value) => onClientChange(value ?? "")}
      />
      <Select
        className="w-full md:max-w-[240px]"
        data={[
          { value: "all", label: "Все" },
          { value: "sent", label: "На стороне" },
          { value: "returned", label: "Возвращены" },
          { value: "overdue", label: "Просрочены" }
        ]}
        label="Состояние"
        value={state}
        onChange={(value) => onStateChange(value ?? "all")}
      />
    </Group>
  );
}
