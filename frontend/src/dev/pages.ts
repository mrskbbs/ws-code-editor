export interface DevPageEntry {
	name: string;
	path: string;
	description: string;
	requiresAuth?: boolean;
}

export const devPages: DevPageEntry[] = [
	{ name: 'Home', path: '/', description: 'Placeholder landing page' },
	{ name: 'Login', path: '/login', description: 'Login form' },
	{ name: 'Signup', path: '/signup', description: 'Signup form' },
	{
		name: 'My Rooms',
		path: '/my/rooms',
		description: 'List of rooms the user belongs to',
		requiresAuth: true,
	},
	{
		name: 'Profile',
		path: '/my/profile',
		description: 'User profile and logout',
		requiresAuth: true,
	},
	{
		name: 'Create Room',
		path: '/room/create',
		description: 'Room creation form',
		requiresAuth: true,
	},
	{
		name: 'Room Editor',
		path: '/room/1/',
		description: 'Client-only collaborative editor shell',
		requiresAuth: true,
	},
	{
		name: 'Room Invite',
		path: '/room/invite/00000000-0000-0000-0000-000000000001',
		description: 'Accept a room invite by token',
		requiresAuth: true,
	},
];