import type { Language, Room, User } from '../types';

export const mockUser: User = {
	id: 1,
	username: 'preview-user',
};

export const mockLanguages: Language[] = [
	{ id: 1, name: 'Python' },
	{ id: 2, name: 'JavaScript' },
	{ id: 3, name: 'C++' },
];

export const mockRooms: Room[] = [
	{
		id: 1,
		title: 'Preview Room',
		code: 'print("hello")',
		invite_token: '00000000-0000-0000-0000-000000000001',
		owner_id: mockUser.id,
		language_id: 1,
		owner: mockUser,
		language: mockLanguages[0],
		members: [mockUser],
	},
	{
		id: 2,
		title: 'Second Room',
		code: 'console.log("hi")',
		invite_token: '00000000-0000-0000-0000-000000000002',
		owner_id: mockUser.id,
		language_id: 2,
		owner: mockUser,
		language: mockLanguages[1],
		members: [mockUser],
	},
];