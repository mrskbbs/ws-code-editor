"use client";

import { RoomStore } from "@/stores/room";
import React, { createContext, useMemo } from "react";

export const RoomContext = createContext<RoomStore>(new RoomStore());

export const RoomContextProvider = ({ children }: { children: React.ReactNode }) => {
    const room = useMemo(() => new RoomStore(), []);
    return <RoomContext.Provider value={room}>{children}</RoomContext.Provider>;
};
