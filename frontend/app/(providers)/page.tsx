"use client";

import React, { RefObject, useCallback, useRef, useState } from "react";
import styles from "./page.module.css";

export default function Home() {
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
