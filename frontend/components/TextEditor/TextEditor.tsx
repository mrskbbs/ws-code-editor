import { io } from "socket.io-client";
import styles from "./TextEditor.module.css";
import { diffApply, diffCreate, jsonKey } from "@/utils";
import React, { Dispatch, memo, RefObject, SetStateAction, useCallback, useEffect, useRef, useState } from "react";
import { observer } from "mobx-react-lite";
import { auth_store } from "@/stores/auth";
import { Indexes } from "./Lines/Lines";
import { Selections } from "./Lines/Selections";
interface ITextEditor {
    label?: string;
    name: string;
    text: string[];
    locations: Map<string, Set<number>>;
    setLocations: (val: Map<string, Set<number>>) => void;
    setText: (val: string[]) => void;
    socket: ReturnType<typeof io>;
}

// Input socket + useState ???
function areEqual(prev: ITextEditor, next: ITextEditor) {
    let text = true;
    let locations = true;

    if (prev.locations.size !== next.locations.size) {
        return false;
    } else {
        for (let [key, value] of prev.locations) {
            if (!next.locations.has(key)) locations = false;
            if (next.locations.get(key) !== value) locations = false;
        }
    }

    if (prev.text.length !== next.text.length) {
        return false;
    } else {
        prev.text.forEach((val, ind) => {
            if (next.text[ind] !== val) text = false;
        });
    }

    return text && locations;
}
export const TextEditor = memo(
    observer(({ label, name, text, setText, locations, setLocations, socket }: ITextEditor) => {
        const staged_changes = useRef(new Map<number, string | null>());
        const last_timeout = useRef(null as ReturnType<typeof setTimeout> | null);

        const code_editor = useRef(null) as RefObject<HTMLDivElement | null>;
        const textarea = useRef(null) as RefObject<HTMLTextAreaElement | null>;

        useEffect(() => {
            socket.on(name, (diffs) => {
                setText(diffApply(text, diffs));
            });
            socket.on(`${name}_location`, (data) => {
                const next = new Map(locations);

                if (data.location.length === 0) next.delete(data.user);
                else next.set(data.user, new Set(data.location));

                setLocations(next);
            });
        }, [text, locations]);

        const stageChanges = useCallback(
            (next: string[]) => {
                if (last_timeout.current !== null) {
                    clearTimeout(last_timeout.current);
                    last_timeout.current = null;
                }

                const diffs = diffCreate(text, next);

                for (let [key, value] of diffs) {
                    staged_changes.current.set(key, value);
                }

                last_timeout.current = setTimeout(() => {
                    socket.emit(name, Object.fromEntries(staged_changes.current.entries()));
                    staged_changes.current.clear();
                    last_timeout.current = null;
                }, 1000);

                return next;
            },
            [text]
        );

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

        const onChangeTextarea = useCallback(
            (e: React.ChangeEvent<HTMLTextAreaElement>) => {
                const new_text = e.currentTarget.value.split("\n");
                e.currentTarget.style.height = `${new_text.length * 1.25}em`;
                stageChanges(new_text);
                setText(new_text);
            },
            [text]
        );

        const onSelectTextarea = useCallback(
            (e: React.SyntheticEvent<HTMLTextAreaElement, Event>) => {
                const sel_start = e.currentTarget.selectionStart;
                const sel_end = e.currentTarget.selectionEnd;
                const indexes = new Set<number>();
                let ind = 0;
                let i = 0;
                for (let line of text) {
                    const new_line_increment = text.length - 1 === i ? 0 : 1;
                    const ind_end = ind + line.length + new_line_increment;

                    if (ind <= sel_start && sel_start < ind_end) indexes.add(i);
                    if (ind <= sel_end && sel_end < ind_end) indexes.add(i);
                    if (sel_start <= ind && ind_end <= sel_end) indexes.add(i);
                    if (ind <= sel_start && sel_end < ind_end) indexes.add(i);

                    if (i === text.length - 1 && (sel_start === ind_end || sel_end === ind_end)) indexes.add(i);

                    ind += line.length + 1;
                    i++;
                }
                console.log(indexes.values());
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

        return (
            <div className={styles.container} style={{ gridArea: name }} onClick={focusTextarea}>
                {label !== undefined && <h2>{label}</h2>}
                <div ref={code_editor} className={styles.code_editor}>
                    <Indexes text_length={text.length} />
                    {locations && <Selections text_length={text.length} locations={locations} />}
                    <textarea
                        style={{ height: `${text.length * 1.25}em` }}
                        wrap="off"
                        spellCheck={false}
                        ref={textarea}
                        id={`${name}-text-editor`}
                        name={`${name}-text-editor`}
                        // defaultValue={text.join("\n")}
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
    }),
    areEqual
);
