import styles from "./Spinner.module.css";

interface ICSpinner {
    text?: string;
}

export const Spinner = ({ text }: ICSpinner) => {
    return (
        <div className={styles.container}>
            <span className={styles.loader}></span>
            {text && <p>{text}...</p>}
        </div>
    );
};
