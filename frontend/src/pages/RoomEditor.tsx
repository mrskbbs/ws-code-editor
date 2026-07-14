import { useEffect, useState } from 'preact/hooks';
import { render } from 'preact';
import { useRoute } from 'preact-iso';
import { useRequireAuth } from '../hooks/useRequireAuth';
import { getRoom } from '../api/rooms';
import { CollaborativeEditor } from '../components/CollaborativeEditor';

export function RoomEditor() {
	const { roomId } = useRoute();
	const { user, loading: authLoading } = useRequireAuth();
	const [title, setTitle] = useState('');
	const [inviteHref, setInviteHref] = useState('');
	const id = Number(roomId);

	useEffect(() => {
		if (!user || !id) return;

		getRoom(id)
			.then((room) => {
				setTitle(room.title);
				setInviteHref(`/room/invite/${room.invite_token}`);
			})
			.catch(() => setTitle('Room'));
	}, [user, id]);

	useEffect(() => {
		if (!user || !id) return;

		const mount = document.getElementById('room-editor-root');
		if (!mount) return;

		render(<CollaborativeEditor roomId={id} />, mount);

		return () => {
			render(null, mount);
		};
	}, [user, id]);

	if (authLoading || !user) {
		return <p>Loading...</p>;
	}

	return (
		<section class="room-editor-page">
			<h1>{title || 'Room'}</h1>
			{inviteHref && (
				<p>
					Invite link: <a href={inviteHref}>{inviteHref}</a>
				</p>
			)}
			<div id="room-editor-root" />
		</section>
	);
}