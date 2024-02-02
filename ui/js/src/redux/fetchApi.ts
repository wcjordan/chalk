import Cookies from 'js-cookie';
import { Platform } from 'react-native';

import { getEnvFlags } from '../helpers';
import { ReduxState } from './types';

const webCsrfToken = Cookies.get('csrftoken');
export function getCsrfToken(getState: () => ReduxState): string {
  return Platform.select({
    native: getState().workspace.csrfToken,
    default: webCsrfToken,
  }) as string;
}

export async function list<T>(apiUri: string): Promise<Array<T>> {
  const response = await fetch(apiUri, getRequestOpts('GET'));
  return handleResponse<Array<T>>(response);
}

export async function patch<T, Q extends { id: number }>(
  apiUri: string,
  entryPatch: Q,
  csrfToken: string,
): Promise<T> {
  const requestOpts = getRequestOpts('PATCH', csrfToken);
  requestOpts.body = JSON.stringify(entryPatch);
  const response = await fetch(`${apiUri}${entryPatch.id}/`, requestOpts);
  return handleResponse<T>(response);
}

export async function create<T, Q>(
  apiUri: string,
  newEntry: Q,
  csrfToken: string,
): Promise<T> {
  return postRequest<T, Q>(apiUri, newEntry, csrfToken);
}

export async function postRequest<T, Q>(
  uri: string,
  data: Q,
  csrfToken: string,
): Promise<T> {
  const requestOpts = getRequestOpts('POST', csrfToken);
  requestOpts.body = JSON.stringify(data);
  const response = await fetch(uri, requestOpts);
  return handleResponse<T>(response);
}

function getRequestOpts(
  method: string,
  csrfToken: string | null = null,
): RequestInit {
  const headers: HeadersInit = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken;
  }

  const credentials: RequestCredentials = Platform.select({
    native: 'include',
    default: 'same-origin',
  });

  return {
    credentials: credentials,
    headers: headers,
    method: method,
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return await response.json();
}

export function getWsRoot(): string {
  const subdomain =
    getEnvFlags().ENVIRONMENT === 'prod' ? 'chalk' : 'chalk-dev';
  const wsroot = Platform.select({
    native: `http://${subdomain}.flipperkid.com/`,
    default: '',
  });
  return wsroot;
}

// Used to exchange login token for session cookie in mobile login flow
export async function completeAuthCallback(token: string) {
  return await fetch(
    `${getWsRoot()}api/todos/auth_callback/?code=${token}`,
    getRequestOpts('GET'),
  );
}
