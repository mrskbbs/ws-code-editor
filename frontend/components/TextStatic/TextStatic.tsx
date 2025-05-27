import { HTMLProps } from "react";
import styles from "./TextStatic.module.css";
import { Line } from "../Line/Line";

interface ITextStatic extends HTMLProps<HTMLDivElement> {
    text: string[];
    label?: string;
}

export const TextStatic = ({ label, text, ...div_props }: ITextStatic) => {
    return (
        <div style={div_props.style} className={styles.container}>
            {label !== undefined && <h2>{label}</h2>}
            <div className={styles.lines_container}>
                {text.map((line, index) => (
                    <p className={index % 2 == 0 ? styles.evenline : styles.oddline}>{line}</p>
                ))}
            </div>
        </div>
    );
};
