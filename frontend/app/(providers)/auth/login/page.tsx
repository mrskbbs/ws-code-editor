"use client";

import { ModalWrapper, ModalWrapperContext } from "@/components/ModalWrapper/ModalWrapper";
import { LoginForm } from "@/forms/LoginForm/LoginForm";
import { useModal } from "@/hooks/useModal";

export default function LoginPage() {
    const { content: modal_content, ...modal } = useModal(false);

    return (
        <>
            <ModalWrapper {...modal}>{modal_content}</ModalWrapper>
            <ModalWrapperContext.Provider value={modal}>
                <LoginForm />
            </ModalWrapperContext.Provider>
        </>
    );
}
