import http, { setAuthTokenGetter } from './httpClient';
import { User } from '../types';

let accessToken: string | null = null;

export const getAccessToken = () => accessToken;
export const setAccessToken = (token: string) => {
  accessToken = token;
};
export const clearAccessToken = () => {
  accessToken = null;
};

// Provide token getter to http client interceptors.
setAuthTokenGetter(getAccessToken);

export const authApi = {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
  async login(email: string, password: string): Promise<{ user: User; access_token: string }> {
    const { data } = await http.post('/auth/login', { email, password });
    return data;
  },
  async logout(): Promise<void> {
    await http.post('/auth/logout');
    clearAccessToken();
  },
  async refresh(): Promise<string> {
    const { data } = await http.post('/auth/refresh');
    return data.access_token;
  },
  async me(): Promise<User> {
    const { data } = await http.get('/auth/me');
    return data;
  },
};

// Helpers used by httpClient dynamic imports to avoid circular refs
export const refreshToken = authApi.refresh;
