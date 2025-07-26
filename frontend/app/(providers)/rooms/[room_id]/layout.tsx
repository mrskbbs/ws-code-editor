"use client";

import { AuthCheck } from "@/components/AuthCheck/AuthCheck";
import { RoomContextProvider } from "@/components/RoomContext";
import { RoomStore } from "@/stores/room";
import { useParams } from "next/navigation";
import React, { createContext } from "react";

export default function RoomLayout({ children }: { children: React.ReactNode }) {
    const room = new RoomStore();
    return (
        <RoomContextProvider value={room}>
            <AuthCheck>{children}</AuthCheck>
        </RoomContextProvider>
    );
}
