import styles from "../TextEditor.module.css";
import { jsonKey, stringToColor } from "@/utils";
import { observer } from "mobx-react-lite";
import { memo } from "react";
interface ICSelections {
    text_length: number;
    locations: Map<string, Set<number>>;
}

export const Selections = observer(({ text_length, locations }: ICSelections) => {
    return (
        <div className={styles.line_selections}>
            {Array.from({ length: text_length }, (_, i) => i).map((index) => {
                const user_selection: string[] = [];
                for (let [user_id, indexes] of locations) {
                    if (indexes.has(index)) user_selection.push(user_id);
                }
                return (
                    <>
                        {user_selection.map((user_id) => (
                            <div
                                key={jsonKey({ index, user_id })}
                                style={{ top: `${1.25 * index}em`, backgroundColor: stringToColor(user_id) }}
                                className={styles.odd_line}
                            />
                        ))}
                    </>
                );
            })}
        </div>
    );
});
