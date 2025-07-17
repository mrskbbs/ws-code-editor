import { io } from "socket.io-client";
import styles from "./TextEditor.module.css";
import { diffApply, diffCreate, jsonKey } from "@/utils";
import React, { Dispatch, RefObject, SetStateAction, useCallback, useEffect, useRef, useState } from "react";
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

    const [locations, setLocation] = useState(new Map<string, Set<number>>()); // TODO: Make a good location storage
    const code_editor = useRef(null) as RefObject<HTMLDivElement | null>;
    const indexes = useRef(null) as RefObject<HTMLDivElement | null>;
    const textarea = useRef(null) as RefObject<HTMLTextAreaElement | null>;

    useEffect(() => {
        socket.on(name, (diffs) => {
            setText((prev) => diffApply(prev, diffs));
        });
        socket.on(`${name}_location`, (data) => {
            setLocation((prev) => {
                const next = new Map(prev);

                if (data.location.length === 0) next.delete(data.user);
                else next.set(data.user, new Set(data.location));

                return next;
            });
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

    const onScrollTextarea = useCallback(
        (e: React.UIEvent<HTMLTextAreaElement, UIEvent>) => {
            e.preventDefault();
            const top_perc = e.currentTarget.scrollTop / e.currentTarget.getBoundingClientRect().height;
            const left_perc = e.currentTarget.scrollLeft / e.currentTarget.getBoundingClientRect().width;
            if (code_editor.current) {
                code_editor.current.scrollBy({
                    top: top_perc * code_editor.current.getBoundingClientRect().height,
                    left: left_perc * code_editor.current.getBoundingClientRect().width,
                });
            }
        },
        [code_editor]
    );

    const onKeyDownTextarea = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Tab") {
            e.preventDefault();
            const val = e.currentTarget.value;
            const start = e.currentTarget.selectionStart;
            const end = e.currentTarget.selectionEnd;
            e.currentTarget.value = val.slice(0, start) + "\t" + val.slice(end, val.length);
            stageChanges(e.currentTarget.value.split("\n"));
        }
    }, []);

    const onChangeTextarea = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const new_text = e.currentTarget.value.split("\n");
        e.currentTarget.style.height = `${new_text.length * 1.25}em`;
        stageChanges(new_text);
    }, []);

    const onSelectTextarea = useCallback(
        (e: React.SyntheticEvent<HTMLTextAreaElement, Event>) => {
            const sel_start = e.currentTarget.selectionStart;
            const sel_end = e.currentTarget.selectionEnd;
            const indexes = new Set<number>();
            let ind = 0;
            let i = 0;
            for (let line of text) {
                const ind_end = ind + line.length + 1;
                if (ind <= sel_start && sel_start < ind_end) indexes.add(i);
                if (sel_start < ind && sel_end > ind_end) indexes.add(i);
                if (ind <= sel_end && sel_end < ind_end) indexes.add(i);
                ind += line.length + 1;
                i++;
            }
            socket.emit(`${name}_location`, [...indexes.values()]);
        },
        [text]
    );
    const focusTextarea = useCallback(() => {
        textarea.current?.focus();
    }, [textarea]);

    const onFocusInTextarea = useCallback((e: React.FocusEvent<HTMLTextAreaElement, Element>) => {
        // TODO MAYBE DELETE
    }, []);

    const onFocusOutTextarea = useCallback((e: React.FocusEvent<HTMLTextAreaElement, Element>) => {
        socket.emit(`${name}_location`, []);
    }, []);

    const renderLines = useCallback(() => {
        const arr: React.ReactNode[] = [];
        for (let [index, line] of text.entries()) {
            const users = [];
            const user_selection = [];
            for (let [user, indexes] of locations) {
                if (indexes.has(index)) {
                    user_selection.push(<div key={jsonKey({ index, user })} className={styles.odd_line} />);
                    users.push(user);
                }
            }
            arr.push(
                <span key={jsonKey({ index: index + 1, users })}>
                    {index + 1}
                    {user_selection}
                </span>
            );
        }
        return arr;
    }, [text, locations]);

    return (
        <div className={styles.container} style={{ gridArea: name }} onClick={focusTextarea}>
            {label !== undefined && <h2>{label}</h2>}
            <div ref={code_editor} className={styles.code_editor}>
                <div ref={indexes} className={styles.line_indexes}>
                    {renderLines()}
                </div>
                <textarea
                    spellCheck={false}
                    ref={textarea}
                    id={`${name}-text-editor`}
                    name={`${name}-text-editor`}
                    defaultValue={text.join("\n")}
                    value={text.join("\n")}
                    onSelect={onSelectTextarea}
                    onScroll={onScrollTextarea}
                    onKeyDown={onKeyDownTextarea}
                    onChange={onChangeTextarea}
                    onFocus={onFocusInTextarea}
                    onBlur={onFocusOutTextarea}
                ></textarea>
            </div>
        </div>
    );
};
