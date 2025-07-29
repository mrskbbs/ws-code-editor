import { deleteRoom } from "@/api/room";
import { ProfilePic } from "@/components/ProfilePic/ProfilePic";
import { auth_store } from "@/stores/auth";
import styles from "./Room.module.css";
import DeleteSVG from "@/public/svg/delete.svg";
import { useRouter } from "next/navigation";
import { useContext } from "react";
import { RoomsFetchContext } from "@/app/(providers)/me/page";

interface ICRoom {
    room: IRoom;
}

export const Room = ({ room }: ICRoom) => {
    const USER_MAX_DISPLAY = 1;
    const router = useRouter();
    const { refetch } = useContext(RoomsFetchContext);
    return (
        <div className={styles.room}>
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
                onClick={() => {
                    router.push(`rooms/${room.id}`);
                }}
            ></div>
            {room.creator.id === auth_store.user?.id && (
                <button
                    className={styles.delete}
                    onClick={() => {
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
