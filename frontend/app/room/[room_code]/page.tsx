"use client";

import { TextEditor } from "@/components/TextEditor/TextEditor";
import { useParams, useRouter } from "next/navigation";
import styles from "./page.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { useWS } from "@/hooks/useWS";

export default function RoomPage() {
    const router = useRouter();
    const { room_code } = useParams();

    // Main app data
    const [code, setCode] = useState(() => [] as string[]);
    const [stdin, setStdin] = useState(() => [] as string[]);
    const [stdout, setStdout] = useState(() => [] as string[]);
    const [is_running, setIsRunning] = useState(() => false);

    // Socket IO
    const { is_connected, is_disconnected, socket } = useWS(`http://localhost:5000/room?room_code=${room_code}`, {
        withCredentials: true,
    });

    useEffect(() => {
        socket.current?.on("connections", (data) => {
            console.log("Conns", data);
        });
        socket.current?.on("run", (data) => {
            console.log("run", data);
            setIsRunning(() => data);
        });
        socket.current?.on("stderr", (data) => {
            console.error(data);
        });
    }, []);

    const runCode = useCallback(() => {
        if (is_running) return;
        socket.current?.emit("run");
    }, [socket]);

    if (!is_connected && !is_disconnected) {
        return <p>Connecting...</p>;
    }
    if (is_disconnected) {
        return <a href="https://www.youtube.com/watch?v=IEDWEhXXfoQ">DISCONNECTED</a>;
    }
    if (socket.current === null) {
        return <p>Socket is null smh</p>;
    }

    return (
        <main className={styles.main_layout}>
            <header style={{ gridArea: "header" }}>
                <h1>Room #{room_code}</h1>
                <div>
                    <p>Connections</p> <div></div>
                </div>
                <button onClick={() => runCode()}>{is_running ? "Cant run" : "Run"}</button>
                <span>
                    <button>Copy invite link</button>
                    <button>Copy room code</button>
                </span>
                <button
                    onClick={() => {
                        socket.current?.disconnect();
                        router.push("/");
                    }}
                >
                    Leave
                </button>
            </header>
            <TextEditor name="code" text={code} setText={setCode} socket={socket.current} />
            <TextEditor name="stdin" text={stdin} setText={setStdin} socket={socket.current} />
            <div style={{ gridArea: "stdout" }}>
                {stdout.map((line) => {
                    return <p>{line}</p>;
                })}
            </div>
        </main>
    );
}
