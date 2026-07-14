import { useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { useAuth } from './useAuth';

export function useRequireAuth() {
	const { user, loading } = useAuth();
	const { route } = useLocation();

	useEffect(() => {
		if (!loading && !user) {
			route('/login');
		}
	}, [loading, user, route]);

	return { user, loading };
}