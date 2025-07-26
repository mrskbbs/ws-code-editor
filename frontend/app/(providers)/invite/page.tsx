"use client";
import { acceptInvite } from "@/api/room";
import { useParams, useRouter, useSearchParams } from "next/navigation";

export default function InvitePage() {
    const router = useRouter();
    const params = useSearchParams();
    const room_id = params.get("room_id");
    const invite_token = params.get("invite_token");

    if (room_id?.toString() === undefined || invite_token?.toString() === undefined) {
        return (
            <div>
                <p>Invalid link</p>
            </div>
        );
    }

    return (
        <div>
            <p>You've been invited to room {room_id}</p>
            <button
                onClick={async () => {
                    acceptInvite(room_id.toString(), invite_token.toString())
                        .then(() => router.push(`/rooms/${room_id}`))
                        .catch((err) => console.error("Invalid invite link"));
                }}
            >
                Accept
            </button>
        </div>
    );
}
