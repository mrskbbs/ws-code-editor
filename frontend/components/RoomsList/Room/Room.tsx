import { deleteRoom } from "@/api/room";
import { ProfilePic } from "@/components/ProfilePic/ProfilePic";
import { auth_store } from "@/stores/auth";
import styles from "./Room.module.css";
import DeleteSVG from "@/public/svg/delete.svg";
import { useRouter } from "next/navigation";
import { RefObject, useContext, useRef } from "react";
import { RoomsFetchContext } from "@/app/(providers)/me/page";

interface ICRoom {
    room: IRoom;
}

export const Room = ({ room }: ICRoom) => {
    const USER_MAX_DISPLAY = 1;
    const router = useRouter();
    const { refetch } = useContext(RoomsFetchContext);
    const container_ref = useRef(null) as RefObject<HTMLDivElement | null>;
    return (
        <div ref={container_ref} className={styles.room}>
            <h2 style={{ gridArea: "name" }}>{room.name}</h2>{" "}
            <p style={{ gridArea: "date" }}>Created at {new Date(room.created_at).toLocaleString()}</p>
            <p style={{ gridArea: "creator" }}>by {room.creator.username}</p>
            <span style={{ gridArea: "contributors" }} className={styles.contributors}>
                {room.users.slice(0, USER_MAX_DISPLAY).map((user) => (
                    <ProfilePic key={user.id} id={user.id} username={user.username} is_username_displayed={true} />
                ))}
                {room.users.length > USER_MAX_DISPLAY ? (
                    <span>+{Math.min(room.users.length - USER_MAX_DISPLAY, 99)}</span>
                ) : (
                    <></>
                )}
            </span>
            <div
                className={styles.room_overlay_btn}
                onMouseDown={() => {
                    if (container_ref.current) container_ref.current.style.backgroundColor = "var(--violet)";
                }}
                onMouseLeave={() => {
                    if (container_ref.current) container_ref.current.style.backgroundColor = "rgba(255, 255, 255, 2%)";
                }}
                onClick={() => {
                    if (container_ref.current) container_ref.current.style.backgroundColor = "rgba(255, 255, 255, 2%)";
                    router.push(`rooms/${room.id}`);
                }}
            ></div>
            {room.creator.id === auth_store.user?.id && (
                <button
                    className={styles.delete}
                    onMouseDown={() => {
                        if (container_ref.current) container_ref.current.style.backgroundColor = "var(--red)";
                    }}
                    onMouseLeave={() => {
                        if (container_ref.current)
                            container_ref.current.style.backgroundColor = "rgba(255, 255, 255, 2%)";
                    }}
                    onClick={() => {
                        if (container_ref.current)
                            container_ref.current.style.backgroundColor = "rgba(255, 255, 255, 2%)";
                        deleteRoom(room.id)
                            .finally(() => refetch())
                            .catch(() => console.error("Failed to delete"));
                    }}
                >
                    <DeleteSVG />
                </button>
            )}
        </div>
    );
};
