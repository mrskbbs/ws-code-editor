"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

export default function SignupPage() {
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
            <h1>Create account</h1>
            <label htmlFor="email">
                Email
                <input required id="email" name="email" type="email" />
            </label>
            <label htmlFor="username">
                Username
                <input required id="username" name="username" type="text" />
            </label>
            <label htmlFor="password">
                Password
                <input required id="password" name="password" type="password" />
            </label>
            <button className="beauty_button">Sign up</button>
            <a href="/auth/login">Already have an account?</a>
        </form>
    );
}
