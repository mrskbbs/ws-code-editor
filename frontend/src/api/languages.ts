import { isDevMockEnabled } from '../dev/flags';
import { mockLanguages } from '../dev/mocks';
import { api } from './client';
import type { Language } from '../types';

export async function getLanguages(): Promise<Language[]> {
	if (isDevMockEnabled()) return mockLanguages;
	const res = await api.get<Language[]>('/languages/');
	return res.data;
}