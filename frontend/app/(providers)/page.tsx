"use client";

import { AuthCheck } from "@/components/AuthCheck/AuthCheck";
import styles from "./page.module.css";
import { observer } from "mobx-react-lite";
import { auth_store } from "@/stores/auth";

function Home() {
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
                <AuthCheck>
                    {auth_store.user === null ? (
                        <p>
                            In order to use this app you need to <a href="/auth/login">log in</a> or{" "}
                            <a href="/auth/signup">create an account</a> first
                        </p>
                    ) : (
                        <p>
                            Now that you're logged in you can <a href="/me">go to your page</a>
                        </p>
                    )}
                </AuthCheck>
            </div>
        </div>
    );
}
export default observer(Home);
