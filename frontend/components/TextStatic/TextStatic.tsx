import { HTMLProps, memo } from "react";
import styles from "./TextStatic.module.css";
import CopySVG from "../../public/svg/copy.svg";
import { observer } from "mobx-react-lite";
import { Line } from "./Line/Line";
import { jsonKey } from "@/utils";

interface ITextStatic extends HTMLProps<HTMLDivElement> {
    text: string[];
    label?: string;
}

function areEqual(prev: ITextStatic, next: ITextStatic) {
    if (prev.text.length !== next.text.length) return false;
    return prev.text.every((val, ind) => next.text[ind] === val);
}

export const TextStatic = memo(
    observer(({ label, text, ...div_props }: ITextStatic) => {
        return (
            <div style={div_props.style} className={styles.container}>
                {label !== undefined && (
                    <span>
                        <h2>{label}</h2>
                        <button onClick={() => navigator.clipboard.writeText(text.join("\n"))}>
                            <CopySVG />
                        </button>
                    </span>
                )}
                <div className={styles.lines_container}>
                    {text.map((line, index) => (
                        <Line key={jsonKey({ line, index })} line={line} index={index} />
                    ))}
                </div>
            </div>
        );
    }),
    areEqual
);
