import { isDevMockEnabled } from '../dev/flags';
import { mockLanguages, mockRooms, mockUser } from '../dev/mocks';
import { api } from './client';
import type { Room, RoomCreate, RoomInviteResponse } from '../types';

export async function getRooms(): Promise<Room[]> {
	if (isDevMockEnabled()) return mockRooms;
	const res = await api.get<Room[]>('/rooms/');
	return res.data;
}

export async function createRoom(data: RoomCreate): Promise<Room> {
	if (isDevMockEnabled()) {
		const language = mockLanguages.find((l) => l.id === data.language_id);
		return {
			id: 99,
			title: data.title,
			code: '',
			invite_token: '00000000-0000-0000-0000-000000000099',
			owner_id: mockUser.id,
			language_id: data.language_id,
			owner: mockUser,
			language,
			members: [mockUser],
		};
	}
	const res = await api.post<Room>('/rooms/', data);
	return res.data;
}

export async function acceptRoomInvite(inviteToken: string): Promise<RoomInviteResponse> {
	if (isDevMockEnabled()) {
		const room = mockRooms.find((r) => r.invite_token === inviteToken) ?? mockRooms[0];
		return { message: `Succesfully joined the room ${room.id}` };
	}
	const res = await api.get<RoomInviteResponse>(`/rooms/invite/${inviteToken}`);
	return res.data;
}

export async function getRoom(roomId: number): Promise<Room> {
	if (isDevMockEnabled()) {
		return (
			mockRooms.find((r) => r.id === roomId) ?? {
				...mockRooms[0],
				id: roomId,
			}
		);
	}
	const res = await api.get<Room>(`/rooms/${roomId}`);
	return res.data;
}