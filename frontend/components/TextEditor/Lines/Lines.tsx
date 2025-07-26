import styles from "../TextEditor.module.css";
import { jsonKey } from "@/utils";
import { observer } from "mobx-react-lite";
import { Selections } from "./Selections";
import { memo } from "react";

interface ICLines {
    text_length: number;
    locations: Map<string, Set<number>>;
}

interface ICIndexes {
    text_length: number;
}

function areEqual(prev: ICIndexes, next: ICIndexes) {
    return prev.text_length === next.text_length;
}

export const Indexes = memo(
    observer(({ text_length }: ICIndexes) => {
        return (
            <div className={styles.line_indexes}>
                {Array.from({ length: text_length }, (_, i) => i).map((index) => {
                    // const user_selection: string[] = [];
                    // for (let [user_id, indexes] of locations) {
                    //     if (indexes.has(index)) user_selection.push(user_id);
                    // }
                    return <span key={jsonKey({ index })}>{index + 1}</span>;
                })}
            </div>
        );
    }),
    areEqual
);
