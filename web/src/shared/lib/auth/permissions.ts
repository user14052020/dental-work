const ADMIN_PERMISSION = "*";

function normalizePermissionCodes(permissionCodes?: string[] | null) {
  if (!permissionCodes?.length) {
    return [];
  }

  const normalized = permissionCodes.filter(Boolean).map((code) => code.trim()).filter(Boolean);
  if (normalized.includes(ADMIN_PERMISSION)) {
    return [ADMIN_PERMISSION];
  }

  return Array.from(new Set(normalized));
}

export function hasPermission(permissionCodes: string[] | null | undefined, requiredCode: string) {
  const normalized = normalizePermissionCodes(permissionCodes);
  return normalized.includes(ADMIN_PERMISSION) || normalized.includes(requiredCode);
}

export function hasAnyPermission(permissionCodes: string[] | null | undefined, requiredCodes?: string[]) {
  if (!requiredCodes?.length) {
    return true;
  }

  return requiredCodes.some((code) => hasPermission(permissionCodes, code));
}
