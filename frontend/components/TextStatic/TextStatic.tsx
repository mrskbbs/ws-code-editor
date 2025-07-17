import { HTMLProps } from "react";
import styles from "./TextStatic.module.css";
import { Line } from "../Line/Line";
import CopySVG from "../../public/svg/copy.svg";
import { observer } from "mobx-react-lite";

interface ITextStatic extends HTMLProps<HTMLDivElement> {
    text: string[];
    label?: string;
}

export const TextStatic = observer(({ label, text, ...div_props }: ITextStatic) => {
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
                    <p key={`${index}${line}`} className={index % 2 == 0 ? styles.evenline : styles.oddline}>
                        {line}
                    </p>
                ))}
            </div>
        </div>
    );
});
