import styles from "./Indexes.module.css";
import { jsonKey } from "@/utils";
import { observer } from "mobx-react-lite";
import { memo } from "react";

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
                    return <span key={jsonKey({ index })}>{index + 1}</span>;
                })}
            </div>
        );
    }),
    areEqual
);
