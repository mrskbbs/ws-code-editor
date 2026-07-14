import { useLocation } from 'preact-iso';
import { AuthForm } from '../components/AuthForm';
import { login } from '../api/auth';

export function Login() {
	const { route, query } = useLocation();
	const next = query.next || '/my/rooms';
	const signupHref = query.next
		? `/signup?next=${encodeURIComponent(query.next)}`
		: '/signup';

	return (
		<section>
			<h1>Login</h1>
			<AuthForm
				submitLabel="Login"
				onSubmit={async (creds) => {
					await login(creds);
					route(next);
				}}
			/>
			<p>
				No account? <a href={signupHref}>Sign up</a>
			</p>
		</section>
	);
}