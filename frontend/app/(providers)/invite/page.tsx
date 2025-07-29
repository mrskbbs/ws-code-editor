"use client";
import styles from "./page.module.css";
import { acceptInvite } from "@/api/room";
import { ErrorDisplay } from "@/components/ErrorDisplay/ErrorDisplay";
import { ModalWrapper } from "@/components/ModalWrapper/ModalWrapper";
import { useModal } from "@/hooks/useModal";
import { useParams, useRouter, useSearchParams } from "next/navigation";

export default function InvitePage() {
    const router = useRouter();
    const params = useSearchParams();
    const room_id = params.get("room_id");
    const invite_token = params.get("invite_token");
    const { content: modal_content, ...modal } = useModal(false);

    if (room_id?.toString() === undefined || invite_token?.toString() === undefined) {
        return (
            <div className={styles.container}>
                <div>Invalid invite link</div>
            </div>
        );
    }

    return (
        <>
            <ModalWrapper {...modal}>{modal_content}</ModalWrapper>
            <div className={styles.container}>
                <p>
                    You've been invited to room <span>{room_id}</span>
                </p>
                <div>
                    <button
                        className={`beauty_button`}
                        onClick={() => {
                            acceptInvite(room_id.toString(), invite_token.toString())
                                .then(() => router.push(`/rooms/${room_id}`))
                                .catch((err) => modal.open(<ErrorDisplay err={err} />));
                        }}
                    >
                        Accept
                    </button>
                    <button
                        className={`beauty_button`}
                        onClick={() => {
                            router.push("/me");
                        }}
                    >
                        Decline
                    </button>
                </div>
            </div>
        </>
    );
}
