import styles from "../TextEditor.module.css";
import { jsonKey } from "@/utils";
import { observer } from "mobx-react-lite";

export const Selections = observer(({ index, user_selection }: { index: number; user_selection: string[] }) => {
    return (
        <>
            {user_selection.map((user_id) => (
                <div key={jsonKey({ index, user_id })} className={styles.odd_line} />
            ))}
        </>
    );
});
