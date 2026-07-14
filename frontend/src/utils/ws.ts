export function encodeUpdate(update: Uint8Array): string {
	let binary = '';
	for (let i = 0; i < update.length; i++) {
		binary += String.fromCharCode(update[i]);
	}
	return btoa(binary);
}

export function decodeUpdate(payload: string): Uint8Array {
	const binary = atob(payload);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}
	return bytes;
}

export function roomWsUrl(roomId: number): string {
	const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
	return `${protocol}//${location.host}/api/v1/rooms/${roomId}/ws`;
}