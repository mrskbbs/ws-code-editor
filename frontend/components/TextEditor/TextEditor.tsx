import { io } from "socket.io-client";
import styles from "./TextEditor.module.css";
import { diffApply, diffCreate } from "@/utils";
import { Dispatch, SetStateAction, useCallback, useEffect, useRef } from "react";
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
    const staged_changes = useRef(new Map<number, string | null>());
    const last_timeout = useRef(null as ReturnType<typeof setTimeout> | null);

    useEffect(() => {
        socket.on(name, (diffs) => {
            setText((prev) => diffApply(prev, diffs));
        });
    }, []);

    const setTextWrapped = useCallback((next: string[]) => {
        setText((prev) => {
            console.log(diffCreate(prev, next));
            socket.emit(name, diffCreate(prev, next));
            return next;
        });
    }, []);

    const stageChanges = useCallback((next: string[]) => {
        setText((prev) => {
            const diffs = diffCreate(prev, next);
            if (last_timeout.current !== null) {
                clearTimeout(last_timeout.current);
                last_timeout.current = null;
            }

            for (let [key, value] of diffs) {
                staged_changes.current.set(key, value);
            }

            last_timeout.current = setTimeout(() => {
                socket.emit(name, Object.fromEntries(staged_changes.current.entries()));
                console.log(staged_changes.current);
                staged_changes.current.clear();
                last_timeout.current = null;
            }, 1000);

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
                    stageChanges(e.currentTarget.value.split("\n"));
                }}
            ></textarea>
        </div>
    );
};
