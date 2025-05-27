import { io } from "socket.io-client";
import styles from "./TextEditor.module.css";
import { diffApply, diffCreate } from "@/utils";
import { Dispatch, SetStateAction, useCallback, useEffect } from "react";
// Input socket + useState ???
export const TextEditor = ({
    label,
    name,
    text,
    setText,
    socket,
}: {
    label?: string;
    name: string;
    text: string[];
    setText: Dispatch<SetStateAction<string[]>>;
    socket: ReturnType<typeof io>;
}) => {
    useEffect(() => {
        socket.on(name, (diffs) => {
            setText((prev) => diffApply(prev, diffs));
        });
    }, []);

    const setTextWrapped = useCallback((next: string[]) => {
        setText((prev) => {
            socket.emit(name, diffCreate(prev, next));
            return next;
        });
    }, []);

    return (
        <div className={styles.container} style={{ gridArea: name }}>
            {label !== undefined && <h2>{label}</h2>}
            <textarea
                id={`${name}-text-editor`}
                name={`${name}-text-editor`}
                defaultValue={text.join("\n")}
                value={text.join("\n")}
                onChange={(e) => {
                    // TODO: maybe a smarter way to send all of them in bulk
                    setTextWrapped(e.currentTarget.value.split("\n"));
                }}
            ></textarea>
        </div>
    );
};
