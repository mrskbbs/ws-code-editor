import styles from "./Line.module.css";

interface ICLine {
    index: number;
    line: string;
}

export const Line = ({ index, line }: ICLine) => {
    return (
        <p key={`${index}${line}`} className={index % 2 == 0 ? styles.evenline : styles.oddline}>
            {line}
        </p>
    );
};
