import { auth_store } from "@/stores/auth";

export const AuthCheck = ({ children }: { children: React.ReactNode }) => {
    if (auth_store.user === null) {
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
};
