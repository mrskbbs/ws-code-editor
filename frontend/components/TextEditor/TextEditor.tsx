import styles from "./TextEditor.module.css";
// Input socket + useState ???

export const TextEditor = ({
    name,
    text,
    setText,
}: {
    name: string;
    text: string[];
    setText: (next: string[]) => void;
}) => {
    return (
        <div className={styles.container} style={{ gridArea: name }}>
            <textarea id={`${name}-text-editor`} name={`${name}-text-editor`}></textarea>
        </div>
    );
};
