import styles from "../TextEditor.module.css";
import { jsonKey } from "@/utils";
import { observer } from "mobx-react-lite";
import { Selections } from "./Selections";

export const Lines = observer(
    ({ text_length, locations }: { text_length: number; locations: Map<string, Set<number>> }) => {
        return (
            <div className={styles.line_indexes}>
                {Array.from({ length: text_length }, (_, i) => i).map((index) => {
                    const user_selection: string[] = [];
                    for (let [user_id, indexes] of locations) {
                        if (indexes.has(index)) user_selection.push(user_id);
                    }
                    return (
                        <span key={jsonKey({ index })}>
                            {index + 1}
                            <Selections
                                key={jsonKey({ index, user_selection })}
                                index={index}
                                user_selection={user_selection}
                            />
                        </span>
                    );
                })}
            </div>
        );
    }
);
