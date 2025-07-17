"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

export default function LoginPage() {
    const router = useRouter();

    const onSubmit = useCallback((e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const form_data = new Map(new FormData(e.currentTarget).entries());
        for (let value of form_data.values()) {
            if (!value) {
                console.error("Invalid field");
                return;
            }
        }
        router.push("/me");
    }, []);

    return (
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
    );
}
