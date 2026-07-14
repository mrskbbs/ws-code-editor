import { useEffect, useState } from 'preact/hooks';
import { useRequireAuth } from '../hooks/useRequireAuth';
import { getRooms } from '../api/rooms';
import { RoomList } from '../components/RoomList';
import type { Room } from '../types';

export function MyRooms() {
	const { user, loading: authLoading } = useRequireAuth();
	const [rooms, setRooms] = useState<Room[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (!user) return;

		setLoading(true);
		getRooms()
			.then(setRooms)
			.catch(() => setError('Failed to load rooms'))
			.finally(() => setLoading(false));
	}, [user]);

	if (authLoading || !user) {
		return <p>Loading...</p>;
	}

	return (
		<section>
			<h1>My Rooms</h1>
			<p>
				<a href="/room/create">Create a room</a>
			</p>
			{loading && <p>Loading rooms...</p>}
			{error && <p class="form-error">{error}</p>}
			{!loading && !error && <RoomList rooms={rooms} />}
		</section>
	);
}