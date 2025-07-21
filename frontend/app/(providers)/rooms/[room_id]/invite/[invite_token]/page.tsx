"use client";
import { acceptInvite } from "@/api/room";
import { useParams, useRouter } from "next/navigation";

export default function InvitePage() {
    const router = useRouter();
    const { room_id, invite_token } = useParams();
    if (room_id?.toString() === undefined || invite_token?.toString() === undefined) {
        return (
            <div>
                <p>Wow, didn't know you could do that</p>
            </div>
        );
    }
    return (
        <div>
            <p>You've been invited to room {room_id}</p>
            <button
                onClick={async () => {
                    acceptInvite(room_id.toString(), invite_token.toString())
                        .then(() => router.push(`/room/${room_id}`))
                        .catch((err) => console.error("Invalid invite link"));
                }}
            >
                Accept
            </button>
        </div>
    );
}
