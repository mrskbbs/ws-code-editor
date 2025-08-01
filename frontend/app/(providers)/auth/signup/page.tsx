"use client";

import { ErrorDisplay } from "@/components/ErrorDisplay/ErrorDisplay";
import { ModalWrapper, ModalWrapperContext } from "@/components/ModalWrapper/ModalWrapper";
import { SignupForm } from "@/forms/SignupForm/SignupForm";
import { useModal } from "@/hooks/useModal";
import { auth_store } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

export default function SignupPage() {
    const router = useRouter();
    const { content: modal_content, ...modal } = useModal(false);

    return (
        <>
            <ModalWrapper {...modal}>{modal_content}</ModalWrapper>
            <ModalWrapperContext.Provider value={modal}>
                <SignupForm />
            </ModalWrapperContext.Provider>
        </>
    );
}
