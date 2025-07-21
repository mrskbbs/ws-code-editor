"use client";

import { TextEditor } from "@/components/TextEditor/TextEditor";
import { useParams, useRouter } from "next/navigation";
import styles from "./page.module.css";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { useWS } from "@/hooks/useWS";
import { diffApply } from "@/utils";
import { createPortal } from "react-dom";
import { Connections } from "@/components/Connections/Connections";
import { ErrorPopups } from "@/components/ErrorPopups/ErrorPopups";
import { TextStatic } from "@/components/TextStatic/TextStatic";
import LeaveSVG from "@/public/svg/leave.svg";
import PlaySVG from "@/public/svg/play.svg";
import ClockSVG from "@/public/svg/clock.svg";
import CopySVG from "@/public/svg/copy.svg";
import { ConnectingSpinner } from "@/components/ConnectingSpinner/ConnectingSpinner";
import { RoomContext } from "./layout";
import { observer } from "mobx-react-lite";
import { BACKEND_URL, FRONTEND_URL } from "@/config";

function RoomPage() {
    const router = useRouter();
    const { room_id } = useParams();
    const room = useContext(RoomContext);

    // Socket IO
    const { is_connected, is_disconnected, socket } = useWS(`${BACKEND_URL}/ws/room?room_id=${room_id}`, {
        withCredentials: true,
    });

    useEffect(() => {
        // Init data
        socket.current?.on("init", (data) => {
            room.name = data.name;
            room.invite_token = `${FRONTEND_URL}/room/${room_id}/invite/${data.invite_token}`;
        });
        socket.current?.on("connections", (data) => {
            room.connections = data;
        });
        socket.current?.on("run", (data) => {
            room.is_running = data;
        });
        socket.current?.on("code", (diffs) => {
            room.code = diffApply(room.code, diffs);
        });
        socket.current?.on("stdin", (diffs) => {
            room.stdin = diffApply(room.stdin, diffs);
        });
        socket.current?.on("stdout", (data) => {
            room.stdout = data;
        });
        socket.current?.on("stderr", (data) => {
            room.stderr = data;
        });
    }, []);

    const runCode = useCallback(() => {
        if (room.is_running) return;
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
            <ErrorPopups text={room.stderr} />
            <main className={styles.main_layout}>
                <header style={{ gridArea: "header" }}>
                    <div>
                        <h1>
                            <span className={styles.sp_weight}>Room {room.name}</span>
                        </h1>
                        <button
                            className={`icon_button ${styles.copy_button}`}
                            onClick={() => navigator.clipboard.writeText(room.invite_token)}
                        >
                            <span>Copy room code</span> <CopySVG />
                        </button>
                        <Connections connections={room.connections} />
                    </div>
                    <div>
                        <button
                            className={`${styles.run_button} ${room.is_running ? styles.running : ""} icon_button`}
                            onClick={() => runCode()}
                        >
                            {room.is_running ? (
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
                <TextEditor
                    label="Code editor"
                    name="code"
                    text={room.code}
                    setText={room.setCode}
                    locations={room.locations_code}
                    setLocations={room.setLocationsCode}
                    socket={socket.current}
                />
                <TextEditor
                    label="Input"
                    name="stdin"
                    text={room.stdin}
                    setText={room.setStdin}
                    locations={room.locations_stdin}
                    setLocations={room.setLocationsStdin}
                    socket={socket.current}
                />
                <TextStatic label="Output" style={{ gridArea: "stdout" }} text={room.stdout} />
            </main>
        </>
    );
}
export default observer(RoomPage);
