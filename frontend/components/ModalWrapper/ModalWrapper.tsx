import React, { createContext, useState } from "react";
import { createPortal } from "react-dom";
import styles from "./ModalWrapper.module.css";
import CloseSVG from "@/public/svg/close.svg";

interface ICModalWrapper {
    children: React.ReactNode;
    is_open: boolean;
    open: (val: React.ReactNode) => void;
    close: () => void;
}

export const ModalWrapperContext = createContext({} as Omit<ICModalWrapper, "children">);

export const ModalWrapper = ({ is_open, open, close, children }: ICModalWrapper) => {
    return (
        <>
            {is_open &&
                createPortal(
                    <div className={styles.container_modal}>
                        <div>
                            <button className={styles.close} onClick={close}>
                                <CloseSVG />
                            </button>
                            <ModalWrapperContext.Provider value={{ is_open, open, close }}>
                                {children}
                            </ModalWrapperContext.Provider>
                        </div>
                    </div>,
                    document.body
                )}
        </>
    );
};
