import { useEffect, useState } from 'preact/hooks';
import { useLocation, useRoute } from 'preact-iso';
import { useAuth } from '../hooks/useAuth';
import { acceptRoomInvite } from '../api/rooms';

function parseRoomId(message: string): number | null {
	const match = message.match(/room (\d+)/);
	return match ? Number(match[1]) : null;
}

export function RoomInvite() {
	const { inviteToken } = useRoute();
	const { user, loading: authLoading } = useAuth();
	const { route } = useLocation();
	const [error, setError] = useState<string | null>(null);

	const returnPath = `/room/invite/${inviteToken}`;
	const loginHref = `/login?next=${encodeURIComponent(returnPath)}`;
	const signupHref = `/signup?next=${encodeURIComponent(returnPath)}`;

	useEffect(() => {
		if (authLoading || !user || !inviteToken) return;

		acceptRoomInvite(inviteToken)
			.then((res) => {
				const roomId = parseRoomId(res.message);
				route(roomId ? `/room/${roomId}/` : '/my/rooms');
			})
			.catch(() => setError('Invalid or expired invite link'));
	}, [authLoading, user, inviteToken, route]);

	if (authLoading) {
		return <p>Loading...</p>;
	}

	if (!user) {
		return (
			<section>
				<h1>Room Invite</h1>
				<p>Log in or sign up to join this room.</p>
				<p>
					<a href={loginHref}>Login</a> · <a href={signupHref}>Sign up</a>
				</p>
			</section>
		);
	}

	if (error) {
		return (
			<section>
				<h1>Room Invite</h1>
				<p class="form-error">{error}</p>
				<p>
					<a href="/my/rooms">Back to my rooms</a>
				</p>
			</section>
		);
	}

	return (
		<section>
			<h1>Room Invite</h1>
			<p>Joining room...</p>
		</section>
	);
}