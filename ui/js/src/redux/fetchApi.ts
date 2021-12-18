import Constants from 'expo-constants';
import Cookies from 'js-cookie';
import { Platform } from 'react-native';

const csrftoken = Cookies.get('csrftoken');
const configs =
  Constants.manifest && Constants.manifest.extra
    ? Constants.manifest.extra
    : {};

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
  const headers: HeadersInit = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
  if (csrftoken) {
    headers['X-CSRFToken'] = csrftoken;
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
  const subdomain = configs.ENVIRONMENT === 'prod' ? 'chalk' : 'chalk-dev';
  const wsroot = Platform.select({
    native: `http://${subdomain}.flipperkid.com/`,
    default: '',
  });
  return wsroot;
}

export async function completeAuthCallback(token: string) {
  const response = await fetch(
    `${getWsRoot()}api/todos/auth_callback/?code=${token}`,
    getRequestOpts('GET'),
  );

  const cookies = response?.headers?.get('set-cookie')?.split(' ');
  return cookies?.find((val) => val.startsWith('sessionid'))?.slice(10, -1);
}
