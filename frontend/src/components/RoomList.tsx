import type { Room } from '../types';

interface RoomListProps {
	rooms: Room[];
}

export function RoomList({ rooms }: RoomListProps) {
	if (rooms.length === 0) {
		return <p>No rooms yet.</p>;
	}

	return (
		<ul class="room-list">
			{rooms.map((room) => (
				<li key={room.id}>
					<a href={`/room/${room.id}/`}>
						{room.title}
						{room.language && ` (${room.language.name})`}
					</a>
				</li>
			))}
		</ul>
	);
}