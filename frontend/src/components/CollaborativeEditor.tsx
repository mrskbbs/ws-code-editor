import { useEffect, useRef, useState } from 'preact/hooks';
import * as Y from 'yjs';
import type { User, WSRoomAction } from '../types';
import { decodeUpdate, encodeUpdate, roomWsUrl } from '../utils/ws';

interface CollaborativeEditorProps {
	roomId: number;
}

export function CollaborativeEditor({ roomId }: CollaborativeEditorProps) {
	const [code, setCode] = useState('');
	const [output, setOutput] = useState('');
	const [members, setMembers] = useState<User[]>([]);
	const [connected, setConnected] = useState(false);
	const docRef = useRef<Y.Doc | null>(null);
	const wsRef = useRef<WebSocket | null>(null);
	const syncingRef = useRef(false);

	useEffect(() => {
		const doc = new Y.Doc();
		const text = doc.getText('content');
		docRef.current = doc;

		const ws = new WebSocket(roomWsUrl(roomId));
		wsRef.current = ws;

		ws.onopen = () => setConnected(true);
		ws.onclose = () => setConnected(false);

		ws.onmessage = (event) => {
			const msg = JSON.parse(event.data) as WSRoomAction;

			switch (msg.action) {
				case 'connect':
					setMembers((prev) => {
						if (prev.some((m) => m.id === msg.payload.id)) return prev;
						return [...prev, msg.payload];
					});
					break;
				case 'disconnect':
					setMembers((prev) => prev.filter((m) => m.id !== msg.payload.id));
					break;
				case 'update_code':
					syncingRef.current = true;
					Y.applyUpdate(doc, decodeUpdate(msg.payload));
					syncingRef.current = false;
					break;
				case 'output':
					setOutput(JSON.stringify(msg.payload, null, 2));
					break;
			}
		};

		const onDocUpdate = (update: Uint8Array, origin: unknown) => {
			if (origin === 'remote' || syncingRef.current) return;
			if (ws.readyState === WebSocket.OPEN) {
				ws.send(
					JSON.stringify({
						action: 'update_code',
						payload: encodeUpdate(update),
					}),
				);
			}
		};

		doc.on('update', onDocUpdate);

		const onTextChange = () => {
			setCode(text.toString());
		};

		text.observe(onTextChange);
		setCode(text.toString());

		return () => {
			text.unobserve(onTextChange);
			doc.off('update', onDocUpdate);
			ws.close();
			doc.destroy();
		};
	}, [roomId]);

	function handleCodeChange(e: Event) {
		const value = (e.target as HTMLTextAreaElement).value;
		const doc = docRef.current;
		if (!doc || syncingRef.current) return;

		const text = doc.getText('content');
		doc.transact(() => {
			text.delete(0, text.length);
			text.insert(0, value);
		});
	}

	function handleRun() {
		const ws = wsRef.current;
		if (ws?.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ action: 'run_code', payload: null }));
		}
	}

	return (
		<div class="editor-layout">
			<div class="editor-toolbar">
				<span>{connected ? 'Connected' : 'Disconnected'}</span>
				<button type="button" onClick={handleRun}>
					Run
				</button>
			</div>
			<div class="editor-members">
				Members: {members.map((m) => m.username).join(', ') || 'none'}
			</div>
			<textarea
				class="editor-textarea"
				value={code}
				onInput={handleCodeChange}
				rows={20}
			/>
			<pre class="editor-output">{output || 'Output will appear here.'}</pre>
		</div>
	);
}