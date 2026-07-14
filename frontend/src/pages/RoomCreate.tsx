import { useEffect, useState } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { useRequireAuth } from '../hooks/useRequireAuth';
import { createRoom } from '../api/rooms';
import { getLanguages } from '../api/languages';
import type { Language } from '../types';

export function RoomCreate() {
	const { user, loading: authLoading } = useRequireAuth();
	const { route } = useLocation();
	const [title, setTitle] = useState('');
	const [languageId, setLanguageId] = useState<number | ''>('');
	const [languages, setLanguages] = useState<Language[]>([]);
	const [loading, setLoading] = useState(true);
	const [submitting, setSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (!user) return;

		getLanguages()
			.then((langs) => {
				setLanguages(langs);
				if (langs.length > 0) {
					setLanguageId(langs[0].id);
				}
			})
			.catch(() => setError('Failed to load languages'))
			.finally(() => setLoading(false));
	}, [user]);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (languageId === '') return;

		setSubmitting(true);
		setError(null);
		try {
			const room = await createRoom({ title, language_id: languageId });
			route(`/room/${room.id}/`);
		} catch {
			setError('Failed to create room');
			setSubmitting(false);
		}
	}

	if (authLoading || !user) {
		return <p>Loading...</p>;
	}

	return (
		<section>
			<h1>Create Room</h1>
			{loading && <p>Loading languages...</p>}
			<form class="room-form" onSubmit={handleSubmit}>
				<label>
					Title
					<input
						type="text"
						value={title}
						onInput={(e) => setTitle((e.target as HTMLInputElement).value)}
						required
					/>
				</label>
				<label>
					Language
					<select
						value={languageId}
						onChange={(e) =>
							setLanguageId(Number((e.target as HTMLSelectElement).value))
						}
						required
					>
						{languages.map((lang) => (
							<option key={lang.id} value={lang.id}>
								{lang.name}
							</option>
						))}
					</select>
				</label>
				{error && <p class="form-error">{error}</p>}
				<button type="submit" disabled={submitting || loading}>
					{submitting ? 'Creating...' : 'Create'}
				</button>
			</form>
		</section>
	);
}