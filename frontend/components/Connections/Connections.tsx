import { useState } from "react";
import styles from "./Connections.module.css";
import { observer } from "mobx-react-lite";
import { stringToColor } from "@/utils";
export const Connections = observer(({ connections }: { connections: IUserData[] }) => {
    const [is_open, setIsOpen] = useState(() => false);
    const USER_MAX_DISPLAY = 5;
    return (
        <div className={styles.container}>
            <p>Connections:</p>
            <div className={styles.conns}>
                {connections.slice(0, USER_MAX_DISPLAY).map((conn) => (
                    <span
                        key={conn.id}
                        className={styles.user_circle}
                        style={{ backgroundColor: stringToColor(conn.id) }}
                    >
                        <p>{conn.username}</p>
                    </span>
                ))}
                {connections.length > USER_MAX_DISPLAY && (
                    <button className={styles.show_btn} onClick={() => setIsOpen((prev) => !prev)}>
                        {is_open ? "Close" : "Show hidden"}
                    </button>
                )}
                {is_open && (
                    <div className={styles.hidden_users}>
                        {connections.slice(USER_MAX_DISPLAY, connections.length).map((conn) => (
                            <span key={conn.id} className={styles.user_circle}>
                                <p>{conn.username}</p>
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
});
