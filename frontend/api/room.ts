import { BACKEND_URL, FETCH_MODE } from "@/config";

export async function getMyRooms() {
    const res = await fetch(`${BACKEND_URL}/rooms`, {
        method: "GET",
        credentials: "include",
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to get rooms");
    return (await res.json()) as IRoom[];
}

export async function createRoom(data: IRoomCreateData) {
    const res = await fetch(`${BACKEND_URL}/rooms`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to create a room");
    return (await res.json()).id as string;
}

export async function deleteRoom(id: string) {
    const res = await fetch(`${BACKEND_URL}/rooms/${id}`, {
        method: "DELETE",
        credentials: "include",
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to delete a room");
}

export async function acceptInvite(id: string, token: string) {
    const res = await fetch(`${BACKEND_URL}/rooms/${id}/invite/${token}`, {
        method: "GET",
        credentials: "include",
        mode: FETCH_MODE,
    });

    if (!res.ok) throw Error("Failed to accept an invite");
}
