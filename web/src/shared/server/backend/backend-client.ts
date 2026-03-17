const fallbackInternalApiUrl = "http://localhost:8100/api/v1";

type BackendRequestOptions = {
  path: string;
  method?: string;
  body?: BodyInit;
  token?: string | null;
  contentType?: string | null;
  search?: string;
};

function getInternalApiUrl() {
  return (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? fallbackInternalApiUrl).replace(
    /\/$/,
    ""
  );
}

function buildBackendUrl(path: string, search?: string) {
  const url = new URL(`${getInternalApiUrl()}${path}`);

  if (search) {
    url.search = search.startsWith("?") ? search.slice(1) : search;
  }

  return url.toString();
}

export async function fetchBackend({
  path,
  method = "GET",
  body,
  token,
  contentType,
  search
}: BackendRequestOptions) {
  return fetch(buildBackendUrl(path, search), {
    method,
    cache: "no-store",
    headers: {
      ...(contentType ? { "Content-Type": contentType } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body
  });
}
