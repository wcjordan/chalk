export async function list(apiUri: string): Promise<any> {
  const response = await fetch(apiUri, getRequestOpts('GET'));
  return handleResponse(response);
}

export async function patch<T extends { id: number }>(
  apiUri: string,
  entryPatch: T,
): Promise<any> {
  const requestOpts = getRequestOpts('PATCH');
  requestOpts.body = JSON.stringify(entryPatch);
  const response = await fetch(`${apiUri}${entryPatch.id}/`, requestOpts);
  return handleResponse(response);
}

export async function create(apiUri: string, newEntry: any): Promise<any> {
  const requestOpts = getRequestOpts('POST');
  requestOpts.body = JSON.stringify(newEntry);
  const response = await fetch(apiUri, requestOpts);
  return handleResponse(response);
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

async function handleResponse(response: Response): Promise<any> {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return await response.json();
}
