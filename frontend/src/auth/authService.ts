import http, { setAuthTokenGetter } from '../../services/httpClient';
import { User } from '../../types';

let accessToken: string | null = null;

export const authService = {
  getAccessToken() {
    return accessToken;
  },
  setAccessToken(token: string) {
    accessToken = token;
  },
  clearAccessToken() {
    accessToken = null;
  },
  async login(email: string, password: string): Promise<{ user: User; access_token: string }> {
    const { data } = await http.post('/auth/login', { email, password });
    return data;
  },
  async logout(): Promise<void> {
    await http.post('/auth/logout');
    accessToken = null;
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

setAuthTokenGetter(() => authService.getAccessToken());
