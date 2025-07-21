import { BACKEND_URL, FETCH_MODE } from "@/config";

export async function getMyself() {
    const res = await fetch(`${BACKEND_URL}/auth/me`, {
        method: "GET",
        credentials: "include",
        mode: FETCH_MODE,
        cache: "force-cache",
    });
    if (!res.ok) throw Error("Failed to get credentials");

    return (await res.json()) as IUserData;
}

export async function signup(data: ISignupData) {
    const res = await fetch(`${BACKEND_URL}/auth/signup`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to create an account");
}

export async function login(data: ILoginData) {
    const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to log in");
}

export async function logout() {
    const res = await fetch(`${BACKEND_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to log out");
}
