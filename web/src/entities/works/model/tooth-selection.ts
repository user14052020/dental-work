export const permanentOdontogramRows = [
  ["18", "17", "16", "15", "14", "13", "12", "11"],
  ["21", "22", "23", "24", "25", "26", "27", "28"],
  ["48", "47", "46", "45", "44", "43", "42", "41"],
  ["31", "32", "33", "34", "35", "36", "37", "38"]
] as const;

export const primaryOdontogramRows = [
  ["55", "54", "53", "52", "51"],
  ["61", "62", "63", "64", "65"],
  ["85", "84", "83", "82", "81"],
  ["71", "72", "73", "74", "75"]
] as const;

export const toothSelectionModeOptions = [
  { label: "Работа", value: "target" },
  { label: "Отсутствует", value: "missing" }
] as const;

export const toothSurfaceOptions = [
  { label: "M", value: "mesial" },
  { label: "D", value: "distal" },
  { label: "V", value: "vestibular" },
  { label: "O", value: "oral" },
  { label: "Oc", value: "occlusal" },
  { label: "I", value: "incisal" }
] as const;

export type ToothSelectionMode = (typeof toothSelectionModeOptions)[number]["value"];
export type ToothSurface = (typeof toothSurfaceOptions)[number]["value"];

export type ToothSelectionItem = {
  tooth_code: string;
  state: ToothSelectionMode;
  surfaces: ToothSurface[];
};

const toothOrder = [
  ...permanentOdontogramRows.flat(),
  ...primaryOdontogramRows.flat()
].reduce<Record<string, number>>((accumulator, toothCode, index) => {
  accumulator[toothCode] = index;
  return accumulator;
}, {});

const surfaceLabels = toothSurfaceOptions.reduce<Record<ToothSurface, string>>((accumulator, option) => {
  accumulator[option.value] = option.label;
  return accumulator;
}, {} as Record<ToothSurface, string>);

export function sortToothSelection(items: ToothSelectionItem[]) {
  return [...items].sort((left, right) => (toothOrder[left.tooth_code] ?? 10_000) - (toothOrder[right.tooth_code] ?? 10_000));
}

export function upsertToothSelectionItem(
  items: ToothSelectionItem[],
  toothCode: string,
  state: ToothSelectionMode
) {
  const currentItem = items.find((item) => item.tooth_code === toothCode);
  if (currentItem?.state === state) {
    return items.filter((item) => item.tooth_code !== toothCode);
  }

  const nextItems = items.filter((item) => item.tooth_code !== toothCode);
  nextItems.push({
    tooth_code: toothCode,
    state,
    surfaces: currentItem?.surfaces ?? []
  });
  return sortToothSelection(nextItems);
}

export function toggleToothSurface(
  items: ToothSelectionItem[],
  toothCode: string,
  surface: ToothSurface
) {
  return sortToothSelection(
    items.map((item) => {
      if (item.tooth_code !== toothCode) {
        return item;
      }

      const hasSurface = item.surfaces.includes(surface);
      return {
        ...item,
        surfaces: hasSurface ? item.surfaces.filter((value) => value !== surface) : [...item.surfaces, surface]
      };
    })
  );
}

export function formatToothSelectionSummary(items: ToothSelectionItem[]) {
  const normalizedItems = sortToothSelection(items);
  if (!normalizedItems.length) {
    return "";
  }

  const selected: string[] = [];
  const missing: string[] = [];

  normalizedItems.forEach((item) => {
    const surfaces = item.surfaces.map((surface) => surfaceLabels[surface]).join(", ");
    const rendered = surfaces ? `${item.tooth_code} (${surfaces})` : item.tooth_code;
    if (item.state === "missing") {
      missing.push(rendered);
      return;
    }
    selected.push(rendered);
  });

  const parts: string[] = [];
  if (selected.length) {
    parts.push(selected.join(", "));
  }
  if (missing.length) {
    parts.push(`отсутствуют: ${missing.join(", ")}`);
  }

  return parts.join("; ");
}
