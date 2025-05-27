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
                Editor where you can edit your code toghether! This is the first finished iteration of this project
                (MVP). But I plan on improving it over the summer , because I do have some interesting ideas
            </p>
            <div className={styles.room_containers}>
                <div>
                    <p>Create your own room</p>
                    <button className="beauty_button" onClick={onClickCreateButton}>
                        Create
                    </button>
                </div>
                <div>
                    <p>Join someone elses room</p>
                    <input
                        ref={input_ref}
                        id="room_code"
                        name="room_code"
                        type="text"
                        placeholder={"Enter room code"}
                    />
                    <button className="beauty_button" onClick={onClickJoinButton}>
                        Join
                    </button>
                </div>
            </div>
        </div>
    );
}
