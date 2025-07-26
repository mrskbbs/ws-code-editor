"use client";
import { auth_store } from "@/stores/auth";
import { observer } from "mobx-react-lite";
import React, { useEffect, useState } from "react";

const DefaultFallback = () => {
    return (
        <>
            <h1>Forbidden</h1>
            <p>
                You are not <a href="/auth/login">logged in</a>
            </p>
        </>
    );
};

export const AuthCheck = observer(
    ({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) => {
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
            if (fallback === undefined) return <DefaultFallback />;
            return <>{fallback}</>;
        }
        return <>{children}</>;
    }
);
