"use client";

import { TextEditor } from "@/components/TextEditor/TextEditor";
import { useParams, useRouter } from "next/navigation";
import styles from "./page.module.css";
import { useCallback, useState } from "react";

export default function RoomPage() {
    const router = useRouter();
    const { room_code } = useParams();

    // Main app data

    const [code, setCode] = useState(() => [] as string[]);
    // Local edit function
    const setCodeWrapped = useCallback((next: string[]) => setCode(next), []);

    const [stdin, setStdin] = useState(() => [] as string[]);
    // Local edit function
    const setStdinWrapped = useCallback((next: string[]) => setStdin(next), []);

    const [stdout, setStdout] = useState(() => [] as string[]);

    return (
        <main className={styles.main_layout}>
            <header style={{ gridArea: "header" }}>
                <h1>Room #{room_code}</h1>
                <div>
                    <p>Connections</p> <div></div>
                </div>
                <span>
                    <button>Copy invite link</button>
                    <button>Copy room code</button>
                </span>
                <button onClick={() => router.push("/")}>Leave</button>
            </header>
            <TextEditor name="code" text={code} setText={setCodeWrapped} />
            <TextEditor name="stdin" text={stdin} setText={setStdinWrapped} />
            <div style={{ gridArea: "stdout" }}>
                {stdout.map((line) => {
                    return <p>{line}</p>;
                })}
            </div>
        </main>
    );
}
