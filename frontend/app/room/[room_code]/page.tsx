"use client";

import { TextEditor } from "@/components/TextEditor/TextEditor";
import { useParams, useRouter } from "next/navigation";
import styles from "./page.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { useWS } from "@/hooks/useWS";
import { diffApply } from "@/utils";
import { createPortal } from "react-dom";
import { Connections } from "@/components/Connections/Connections";
import { ErrorPopups } from "@/components/ErrorPopups/ErrorPopups";
import { TextStatic } from "@/components/TextStatic/TextStatic";
import LeaveSVG from "../../../public/svg/leave.svg";
import PlaySVG from "../../../public/svg/play.svg";
import ClockSVG from "../../../public/svg/clock.svg";
import CopySVG from "../../../public/svg/copy.svg";
import { ConnectingSpinner } from "@/components/ConnectingSpinner/ConnectingSpinner";

export default function RoomPage() {
    const router = useRouter();
    const { room_code } = useParams();

    // Main app data
    const [code, setCode] = useState(() => [""] as string[]);
    const [stdin, setStdin] = useState(() => [""] as string[]);
    const [stdout, setStdout] = useState(() => [] as string[]);
    const [stderr, setStderr] = useState(() => [] as string[]);
    const [connections, setConnections] = useState(() => [] as string[]);
    const [is_running, setIsRunning] = useState(() => false);

    // Socket IO
    const { is_connected, is_disconnected, socket } = useWS(`http://localhost:5000/room?room_code=${room_code}`, {
        withCredentials: true,
    });

    useEffect(() => {
        // Init data
        socket.current?.on("connections", (data) => {
            setConnections(() => data);
        });
        socket.current?.on("run", (data) => {
            setIsRunning(() => data);
        });
        socket.current?.on("code", (diffs) => {
            setCode((prev) => diffApply(prev, diffs));
        });
        socket.current?.on("stdin", (diffs) => {
            setStdin((prev) => diffApply(prev, diffs));
        });
        socket.current?.on("stdout", (data) => {
            setStdout(() => data);
        });
        socket.current?.on("stderr", (data) => {
            setStderr(() => data);
        });
    }, []);

    const runCode = useCallback(() => {
        if (is_running) return;
        socket.current?.emit("run");
    }, [socket]);

    const leaveRoom = useCallback(() => {
        socket.current?.disconnect();
        router.push("/");
    }, [socket]);

    if (!is_connected && !is_disconnected) {
        return <ConnectingSpinner />;
    }
    if (is_disconnected) {
        return (
            <div className={styles.dicsonnect_container}>
                <h1>You've been disconnected</h1>
                <button className="beauty_button" onClick={() => router.push("/")}>
                    Return to main page
                </button>
            </div>
        );
    }
    if (socket.current === null) {
        return <p>Socket is null smh</p>;
    }

    return (
        <>
            <ErrorPopups text={stderr} />
            <main className={styles.main_layout}>
                <header style={{ gridArea: "header" }}>
                    <div>
                        <h1>
                            <span className={styles.sp_weight}>Room</span> {room_code}
                        </h1>
                        <button
                            className={`icon_button ${styles.copy_button}`}
                            onClick={() => navigator.clipboard.writeText(room_code as string)}
                        >
                            <span>Copy room code</span> <CopySVG />
                        </button>
                        <Connections connections={connections} />
                    </div>
                    <div>
                        <button
                            className={`${styles.run_button} ${is_running ? styles.running : ""} icon_button`}
                            onClick={() => runCode()}
                        >
                            {is_running ? (
                                <>
                                    <ClockSVG />
                                    <p>Running...</p>
                                </>
                            ) : (
                                <>
                                    <PlaySVG />
                                    <p>Run</p>
                                </>
                            )}
                        </button>
                        <button className={`icon_button`} onClick={() => leaveRoom()}>
                            <LeaveSVG />
                            <p>Leave room</p>
                        </button>
                    </div>
                </header>
                <TextEditor label="Code editor" name="code" text={code} setText={setCode} socket={socket.current} />
                <TextEditor label="Input" name="stdin" text={stdin} setText={setStdin} socket={socket.current} />
                <TextStatic label="Output" style={{ gridArea: "stdout" }} text={stdout} />
            </main>
        </>
    );
}
