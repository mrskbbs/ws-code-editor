import type { ComponentChildren } from 'preact';
import { useAuth } from '../hooks/useAuth';
import { logout } from '../api/auth';
import { useLocation } from 'preact-iso';

interface LayoutProps {
	children: ComponentChildren;
}

export function Layout({ children }: LayoutProps) {
	const { user, loading, refresh } = useAuth();
	const { route } = useLocation();

	async function handleLogout() {
		await logout();
		await refresh();
		route('/login');
	}

	return (
		<div class="app-layout">
			<header class="app-header">
				<nav class="app-nav">
					{import.meta.env.DEV && <a href="/dev/preview">Dev Preview</a>}
					<a href="/">Home</a>
					{user && (
						<>
							<a href="/my/rooms">My Rooms</a>
							<a href="/room/create">Create Room</a>
							<a href="/my/profile">Profile</a>
						</>
					)}
					{!loading && !user && <a href="/login">Login</a>}
					{!loading && !user && <a href="/signup">Signup</a>}
					{user && (
						<button type="button" onClick={handleLogout}>
							Logout
						</button>
					)}
				</nav>
			</header>
			<main class="app-main">{children}</main>
		</div>
	);
}