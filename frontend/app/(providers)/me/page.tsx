"use client";

import styles from "./page.module.css";
import { deleteRoom, getMyRooms } from "@/api/room";
import { RoomCreate } from "@/components/RoomCreate/RoomCreate";
import { auth_store } from "@/stores/auth";
import { stringToColor } from "@/utils";
import { useQuery } from "@tanstack/react-query";
import { observer } from "mobx-react-lite";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createPortal } from "react-dom";

function MePage() {
    const USER_MAX_DISPLAY = 1;
    const router = useRouter();
    const { data: rooms, isLoading, refetch } = useQuery({ queryFn: getMyRooms, queryKey: ["my", "rooms"] });
    const [is_open, setIsOpen] = useState(() => false);

    if (auth_store.user === null) return;

    return (
        <div className={styles.container}>
            {is_open &&
                createPortal(
                    <div>
                        <button onClick={() => setIsOpen(() => false)}>x</button>
                        <RoomCreate />
                    </div>,
                    document.body
                )}
            <div className={styles.user_header}>
                <span
                    className={styles.avatar}
                    style={{ backgroundColor: stringToColor(auth_store.user.id), gridArea: "av" }}
                ></span>
                <h2 style={{ gridArea: "un" }}>{auth_store.user.username}</h2>
                <p className={styles.user_id} style={{ gridArea: "id" }}>
                    {auth_store.user.id}
                </p>
                <button style={{ gridArea: "lg" }}>Logout</button>
            </div>

            <div className={styles.rooms_header}>
                <h1>Your rooms</h1>
                <button onClick={() => setIsOpen(() => true)}>New room</button>
            </div>
            <div className={styles.rooms}>
                {isLoading ? (
                    <p>Loading...</p>
                ) : rooms === undefined ? (
                    <p>Failed to fetch rooms</p>
                ) : (
                    rooms.map((room) => (
                        <div className={styles.room} key={room.id}>
                            <h2 style={{ gridArea: "name" }}>{room.name}</h2>{" "}
                            <p style={{ gridArea: "date" }}>Created at {new Date(room.created_at).toLocaleString()}</p>
                            <p style={{ gridArea: "creator" }}>by {room.creator.username}</p>
                            <span style={{ gridArea: "contributors" }} className={styles.contributors}>
                                {room.users.slice(0, USER_MAX_DISPLAY).map((user) => (
                                    <span
                                        key={user.id}
                                        style={{ height: "3em", background: stringToColor(user.id) }}
                                        className={styles.avatar}
                                    ></span>
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
                                    style={{ gridArea: "delete", zIndex: "2", justifySelf: "end" }}
                                    onClick={() => {
                                        deleteRoom(room.id)
                                            .finally(() => refetch())
                                            .catch(() => console.error("Failed to delete"));
                                    }}
                                >
                                    Delete
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default observer(MePage);
