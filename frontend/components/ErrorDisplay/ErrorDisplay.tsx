import styles from "./ErrorDisplay.module.css";

interface ICErrorDisplay {
    err: Error;
}

export const ErrorDisplay = ({ err }: ICErrorDisplay) => {
    return (
        <div className={styles.container}>
            <h2>Error occured</h2>
            <hr />
            <p>{err.message}</p>
        </div>
    );
};
