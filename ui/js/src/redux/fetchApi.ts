export async function list<T>(apiUri: string): Promise<Array<T>> {
  const response = await fetch(apiUri, getRequestOpts('GET'));
  return handleResponse<Array<T>>(response);
}

export async function patch<T, Q extends { id: number }>(
  apiUri: string,
  entryPatch: Q,
): Promise<T> {
  const requestOpts = getRequestOpts('PATCH');
  requestOpts.body = JSON.stringify(entryPatch);
  const response = await fetch(`${apiUri}${entryPatch.id}/`, requestOpts);
  return handleResponse<T>(response);
}

export async function create<T, Q>(apiUri: string, newEntry: Q): Promise<T> {
  const requestOpts = getRequestOpts('POST');
  requestOpts.body = JSON.stringify(newEntry);
  const response = await fetch(apiUri, requestOpts);
  return handleResponse<T>(response);
}

function getRequestOpts(method: string): RequestInit {
  return {
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    method: method,
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return await response.json();
}
