import { SocketOptions } from "dgram";
import { useRef, useEffect, useState } from "react";
import { io, ManagerOptions } from "socket.io-client";

export function useWS(uri: string, opts?: Partial<ManagerOptions & SocketOptions> | undefined) {
    const socket = useRef<ReturnType<typeof io> | null>(null);
    const [is_connected, setIsConnected] = useState(() => false);
    const [is_disconnected, setIsDisconnected] = useState(() => false);

    useEffect(() => {
        if (socket.current !== null) return;

        socket.current = io(uri, opts);

        socket.current?.on("connect", () => {
            console.log(`Succesfully connected`);
            setIsConnected(() => true);
            setIsDisconnected(() => false);
        });

        socket.current?.on("disconnect", () => {
            console.log(`Succesfully disconnected`);
            setIsConnected(() => false);
            setIsDisconnected(() => true);
        });
    }, []);

    return {
        socket,
        is_connected,
        is_disconnected,
    };
}
