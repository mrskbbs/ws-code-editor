import { useCallback, useEffect, useState } from 'preact/hooks';
import { getAuth } from '../api/auth';
import type { User } from '../types';

export function useAuth() {
	const [user, setUser] = useState<User | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const refresh = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const authUser = await getAuth();
			setUser(authUser);
		} catch {
			setUser(null);
			setError('Unauthorized');
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		refresh();
	}, [refresh]);

	return { user, loading, error, refresh };
}