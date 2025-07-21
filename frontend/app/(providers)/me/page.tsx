"use client";

import { getMyRooms } from "@/api/room";
import { RoomCreate } from "@/components/RoomCreate/RoomCreate";
import { auth_store } from "@/stores/auth";
import { useQuery } from "@tanstack/react-query";
import { observer } from "mobx-react-lite";

function MePage() {
    const { data: rooms, isLoading } = useQuery({ queryFn: getMyRooms, queryKey: ["my", "rooms"] });
    return (
        <div>
            <RoomCreate />
            {isLoading ? (
                <p>Loading...</p>
            ) : rooms === undefined ? (
                <p>Failed to fetch rooms</p>
            ) : (
                rooms.map((room) => (
                    <span key={room.id}>
                        <a href={`/room/${room.id}`}></a>
                    </span>
                ))
            )}
        </div>
    );
}

export default observer(MePage);
