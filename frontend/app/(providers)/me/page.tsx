"use client";

import { deleteRoom, getMyRooms } from "@/api/room";
import { RoomCreate } from "@/components/RoomCreate/RoomCreate";
import { auth_store } from "@/stores/auth";
import { useQuery } from "@tanstack/react-query";
import { observer } from "mobx-react-lite";
import { useState } from "react";
import { createPortal } from "react-dom";

function MePage() {
    const { data: rooms, isLoading, refetch } = useQuery({ queryFn: getMyRooms, queryKey: ["my", "rooms"] });
    const [is_open, setIsOpen] = useState(() => false);
    return (
        <div>
            <button onClick={() => setIsOpen(() => true)}>+</button>
            {is_open &&
                createPortal(
                    <div>
                        <button onClick={() => setIsOpen(() => false)}>x</button>
                        <RoomCreate />
                    </div>,
                    document.body
                )}
            {isLoading ? (
                <p>Loading...</p>
            ) : rooms === undefined ? (
                <p>Failed to fetch rooms</p>
            ) : (
                rooms.map((room) => (
                    <span key={room.id}>
                        <a href={`/rooms/${room.id}`}>
                            {room.name} {room.created_at}
                        </a>
                        <button
                            onClick={() => {
                                deleteRoom(room.id)
                                    .finally(() => refetch())
                                    .catch(() => console.error("Failed to delete"));
                            }}
                        >
                            Delete
                        </button>
                    </span>
                ))
            )}
        </div>
    );
}

export default observer(MePage);
