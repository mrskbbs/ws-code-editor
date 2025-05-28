import { useEffect, useRef, useState } from "react";
import styles from "./ConnectingSpinner.module.css";

export const ConnectingSpinner = () => {
    const [count, setCount] = useState(() => 0);
    useEffect(() => {
        setInterval(() => {
            setCount((prev) => {
                if (prev + 1 > 3) return 0;
                return prev + 1;
            });
        }, 1000);
    }, []);
    return (
        <div className={styles.container}>
            <span className={styles.loader}></span>
            <p>Connecting{".".repeat(count)}</p>
        </div>
    );
};
