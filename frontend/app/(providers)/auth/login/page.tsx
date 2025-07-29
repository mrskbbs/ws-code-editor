"use client";

import { ErrorDisplay } from "@/components/ErrorDisplay/ErrorDisplay";
import { ModalWrapper } from "@/components/ModalWrapper/ModalWrapper";
import { useModal } from "@/hooks/useModal";
import { auth_store } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

export default function LoginPage() {
    const router = useRouter();
    const { content: modal_content, ...modal } = useModal(false);
    const onSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const form_data = new Map(new FormData(e.currentTarget).entries());
        const payload: any = {};
        try {
            for (let [key, value] of form_data.entries()) {
                if (!value) {
                    throw Error("Invalid field");
                }

                payload[key] = value.toString();
            }
            await auth_store.login(payload as ILoginData);
            router.prefetch("/me");
            router.push("/me");
        } catch (err) {
            if (err instanceof Error) modal.open(<ErrorDisplay err={err} />);
        }
    }, []);

    return (
        <>
            <ModalWrapper {...modal}>{modal_content}</ModalWrapper>
            <form onSubmit={onSubmit}>
                <h1>Log in</h1>
                <label htmlFor="email">
                    Email
                    <input required id="email" name="email" type="email" />
                </label>
                <label htmlFor="password">
                    Password
                    <input required id="password" name="password" type="password" />
                </label>
                <button className="beauty_button">Log in</button>
                <a href="/auth/signup">Don't have an account?</a>
            </form>
        </>
    );
}
