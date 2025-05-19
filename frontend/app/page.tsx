"use client";

import { useRouter } from "next/navigation";
import React, { RefObject, useCallback, useRef } from "react";
import styles from "./page.module.css";

export default function Home() {
    const router = useRouter();

    const input_ref = useRef<null | HTMLInputElement>(null);

    const onClickJoinButton = useCallback(() => {
        if (input_ref.current === undefined || input_ref.current === null || input_ref.current.value.length === 0) {
            // TODO: handle error
            console.error("Input field is empty");
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
            <h1>
                Websocket Code Editor
                <hr />
            </h1>
            <p>
                Bro you can edit code together, it's like... <span className="italic">cool</span>
            </p>
            <div className="horizontal">
                <div className={styles.room_containers}>
                    <p>Create your own room</p>
                    <button onClick={onClickCreateButton}>Create</button>
                </div>
                <div className={styles.room_containers}>
                    <p>Join someone elses room</p>
                    <input ref={input_ref} id="room_code" name="room_code" type="text" />
                    <button onClick={onClickJoinButton}>Join</button>
                </div>
            </div>
        </div>
    );
}
