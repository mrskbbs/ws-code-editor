export interface User {
	id: number;
	username: string;
}

export interface UserCreds {
	username: string;
	password: string;
}

export interface Language {
	id: number;
	name: string;
}

export interface Room {
	id: number;
	title: string;
	code: string;
	invite_token: string;
	owner_id: number;
	language_id: number;
	owner?: User;
	members?: User[];
	language?: Language;
}

export interface RoomCreate {
	title: string;
	language_id: number;
}

export interface RoomInviteResponse {
	message: string;
}

export type WSRoomAction =
	| { action: 'connect'; payload: User }
	| { action: 'disconnect'; payload: User }
	| { action: 'update_code'; payload: string }
	| { action: 'output'; payload: unknown }
	| { action: 'run_code'; payload?: null };