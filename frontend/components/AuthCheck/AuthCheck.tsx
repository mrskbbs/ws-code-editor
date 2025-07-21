"use client";
import { auth_store } from "@/stores/auth";
import { observer } from "mobx-react-lite";
import { useEffect, useState } from "react";

export const AuthCheck = observer(({ children }: { children: React.ReactNode }) => {
    const [is_loading, setIsLoading] = useState(true);
    const [is_error, setIsError] = useState(null as string | null);

    useEffect(() => {
        auth_store
            .update()
            .then(() => {
                setIsLoading(() => false);
            })
            .catch((err: Error) => {
                setIsError(() => err.message);
            })
            .finally(() => {
                setIsLoading(() => false);
            });
    }, []);

    if (is_loading) {
        return <p>Loading...</p>;
    }
    if (is_error) {
        return (
            <>
                <h1>Forbidden</h1>
                <p>
                    You are not <a href="/auth/login">logged in</a>
                </p>
            </>
        );
    }
    return <>{children}</>;
});
