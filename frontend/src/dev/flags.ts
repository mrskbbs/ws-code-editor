export const DEV_MOCK_KEY = '__dev_mock';

export function isDevMockEnabled(): boolean {
	if (!import.meta.env.DEV) return false;

	if (typeof window === 'undefined') return false;

	if (localStorage.getItem(DEV_MOCK_KEY) === '1') return true;

	return new URLSearchParams(location.search).has('__dev_mock');
}

export function setDevMockEnabled(enabled: boolean): void {
	if (!import.meta.env.DEV) return;

	if (enabled) {
		localStorage.setItem(DEV_MOCK_KEY, '1');
	} else {
		localStorage.removeItem(DEV_MOCK_KEY);
	}
}