import { useState } from "react";
import styles from "./Connections.module.css";
import { observer } from "mobx-react-lite";
import { stringToColor } from "@/utils";
export const Connections = observer(({ connections }: { connections: IUserData[] }) => {
    const [is_open, setIsOpen] = useState(() => false);
    const SLICE_NUM = 5;
    return (
        <div className={styles.container}>
            <p>Connections:</p>
            <div className={styles.conns}>
                {connections.slice(0, SLICE_NUM).map((conn) => (
                    <span
                        key={conn.id}
                        className={styles.user_circle}
                        style={{ backgroundColor: stringToColor(conn.id) }}
                    >
                        <p>{conn.username}</p>
                    </span>
                ))}
                {connections.length > SLICE_NUM && (
                    <button className={styles.show_btn} onClick={() => setIsOpen((prev) => !prev)}>
                        {is_open ? "Close" : "Show hidden"}
                    </button>
                )}
                {is_open && (
                    <div className={styles.hidden_users}>
                        {connections.slice(SLICE_NUM, connections.length).map((conn) => (
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
