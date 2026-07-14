import { useLocation } from 'preact-iso';
import { AuthForm } from '../components/AuthForm';
import { signup } from '../api/auth';

export function Signup() {
	const { route, query } = useLocation();
	const next = query.next || '/my/rooms';
	const loginHref = query.next
		? `/login?next=${encodeURIComponent(query.next)}`
		: '/login';

	return (
		<section>
			<h1>Signup</h1>
			<AuthForm
				submitLabel="Sign up"
				onSubmit={async (creds) => {
					await signup(creds);
					route(next);
				}}
			/>
			<p>
				Already have an account? <a href={loginHref}>Login</a>
			</p>
		</section>
	);
}