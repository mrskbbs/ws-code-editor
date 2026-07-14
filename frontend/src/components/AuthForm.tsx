import { useState } from 'preact/hooks';
import type { UserCreds } from '../types';

interface AuthFormProps {
	submitLabel: string;
	onSubmit: (creds: UserCreds) => Promise<void>;
	error?: string | null;
}

export function AuthForm({ submitLabel, onSubmit, error }: AuthFormProps) {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [submitting, setSubmitting] = useState(false);
	const [localError, setLocalError] = useState<string | null>(null);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		setSubmitting(true);
		setLocalError(null);
		try {
			await onSubmit({ username, password });
		} catch {
			setLocalError('Authentication failed');
		} finally {
			setSubmitting(false);
		}
	}

	return (
		<form class="auth-form" onSubmit={handleSubmit}>
			<label>
				Username
				<input
					type="text"
					value={username}
					onInput={(e) => setUsername((e.target as HTMLInputElement).value)}
					required
				/>
			</label>
			<label>
				Password
				<input
					type="password"
					value={password}
					onInput={(e) => setPassword((e.target as HTMLInputElement).value)}
					required
				/>
			</label>
			{(error || localError) && <p class="form-error">{error || localError}</p>}
			<button type="submit" disabled={submitting}>
				{submitting ? 'Submitting...' : submitLabel}
			</button>
		</form>
	);
}