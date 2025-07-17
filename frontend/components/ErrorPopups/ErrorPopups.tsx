import { createPortal } from "react-dom";
import styles from "./ErrorPopups.module.css";
import CopySVG from "../../public/svg/copy.svg";
import CloseSVG from "../../public/svg/close.svg";
import { useEffect, useState } from "react";
import { observer } from "mobx-react-lite";

export const ErrorPopups = observer(({ text }: { text: string[] }) => {
    const [is_open, setIsOpen] = useState(() => true);
    useEffect(() => {
        setIsOpen(() => true);
    }, [text]);
    return (
        <>
            {createPortal(
                <>
                    {is_open && text.length > 0 && (
                        <div className={styles.container}>
                            <div>
                                <button onClick={() => navigator.clipboard.writeText(text.join("\n"))}>
                                    <CopySVG />
                                </button>
                                <button onClick={() => setIsOpen(() => false)}>
                                    <CloseSVG />
                                </button>
                            </div>
                            <h1>Error occured</h1>
                            <hr />
                            {text.map((line) => (
                                <p>{line}</p>
                            ))}
                        </div>
                    )}
                </>,
                document.body
            )}
        </>
    );
});
