import { useLocation } from 'preact-iso';
import { useRequireAuth } from '../hooks/useRequireAuth';
import { logout } from '../api/auth';

export function MyProfile() {
	const { user, loading } = useRequireAuth();
	const { route } = useLocation();

	async function handleLogout() {
		await logout();
		route('/login');
	}

	if (loading || !user) {
		return <p>Loading...</p>;
	}

	return (
		<section>
			<h1>Profile</h1>
			<p>Username: {user.username}</p>
			<button type="button" onClick={handleLogout}>
				Logout
			</button>
		</section>
	);
}