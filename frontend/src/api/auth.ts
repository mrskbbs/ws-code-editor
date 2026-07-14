import { isDevMockEnabled } from '../dev/flags';
import { mockUser } from '../dev/mocks';
import { api } from './client';
import type { User, UserCreds } from '../types';

export async function getAuth(): Promise<User> {
	if (isDevMockEnabled()) return mockUser;
	const res = await api.get<User>('/auth/');
	return res.data;
}

export async function login(creds: UserCreds): Promise<User> {
	if (isDevMockEnabled()) return mockUser;
	const res = await api.post<User>('/auth/login', creds);
	return res.data;
}

export async function signup(creds: UserCreds): Promise<User> {
	if (isDevMockEnabled()) return mockUser;
	const res = await api.post<User>('/auth/signup', creds);
	return res.data;
}

export async function logout(): Promise<void> {
	if (isDevMockEnabled()) return;
	await api.post('/auth/logout');
}