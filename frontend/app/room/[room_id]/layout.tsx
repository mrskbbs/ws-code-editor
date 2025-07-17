"use client";

import { RoomStore } from "@/stores/room";
import { useParams } from "next/navigation";
import React, { createContext } from "react";

export const RoomContext = createContext<RoomStore>(new RoomStore());

export default function RoomLayout({ children }: { children: React.ReactNode }) {
    const room = new RoomStore();
    return <RoomContext.Provider value={room}>{children}</RoomContext.Provider>;
}
