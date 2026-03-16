import { Button, Group, Switch } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type ExecutorsToolbarProps = {
  search: string;
  activeOnly: boolean;
  onSearchChange: (value: string) => void;
  onActiveOnlyChange: (value: boolean) => void;
  onCreate: () => void;
};

export function ExecutorsToolbar({
  search,
  activeOnly,
  onSearchChange,
  onActiveOnlyChange,
  onCreate
}: ExecutorsToolbarProps) {
  return (
    <Group justify="space-between">
      <SearchField
        className="flex-1"
        placeholder="Поиск по ФИО, телефону, эл. почте, специализации, комментарию"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Switch checked={activeOnly} label="Только активные" onChange={(event) => onActiveOnlyChange(event.currentTarget.checked)} />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate}>
        Новый исполнитель
      </Button>
    </Group>
  );
}
