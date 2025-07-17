"use client";

import { useRouter } from "next/navigation";
import React, { RefObject, useCallback, useRef, useState } from "react";
import styles from "./page.module.css";

export default function Home() {
    const router = useRouter();

    const input_ref = useRef<null | HTMLInputElement>(null);
    const [error, setError] = useState(() => null as string | null);
    const onClickJoinButton = useCallback(() => {
        if (input_ref.current === undefined || input_ref.current === null || input_ref.current.value.length === 0) {
            setError(() => "Room code field can't be empty");
            return;
        }

        router.push(`/room/${input_ref.current.value}`);
    }, [input_ref]);

    const onClickCreateButton = useCallback(() => {
        //TODO: backend linking
        router.push("/room/sample_code");
    }, []);

    return (
        <div className={styles.container}>
            <h1>Websocket Code Editor</h1>
            <hr />
            <p>
                Editor where you can edit your code toghether! This is might be the final iteration for now, but who
                knows :)
            </p>
            <hr />
            <div>
                <p>
                    In order to use this app you need to <a href="/auth/login">log in</a> or{" "}
                    <a href="/auth/signup">create an account</a> first
                </p>
                <p>
                    Now that you're logged in you can <a href="/me">go to your page</a>
                </p>
            </div>
        </div>
    );
}
