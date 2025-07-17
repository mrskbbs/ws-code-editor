"use client";

import { getMyRooms } from "@/api/room";
import { useQuery } from "@tanstack/react-query";

export default function MePage() {
    const { data: rooms, isLoading } = useQuery({ queryFn: getMyRooms, queryKey: ["my", "rooms"] });
    return (
        <div>
            <div>
                <input id="name" name="name" type="text" />
                <button>Create room</button>
            </div>
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
