"use client";

import { RoomStore } from "@/stores/room";
import React, { createContext, useMemo } from "react";

export const RoomContext = createContext<RoomStore>(new RoomStore());

export const RoomContextProvider = ({ children, value }: { children: React.ReactNode; value: RoomStore }) => {
    return <RoomContext.Provider value={value}>{children}</RoomContext.Provider>;
};
