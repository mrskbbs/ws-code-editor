import styles from "./Line.module.css";
export const Line = ({ index, text }: { index: number; text: string }) => {
    return (
        <>
            <span>{index}</span>
            <span>{text}</span>
        </>
    );
};
