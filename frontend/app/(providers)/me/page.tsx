"use client";

import styles from "./page.module.css";
import { getMyRooms } from "@/api/room";
import { useQuery } from "@tanstack/react-query";
import { observer } from "mobx-react-lite";
import { createContext, useState } from "react";
import AddBoxSVG from "@/public/svg/addbox.svg";
import { RoomsList } from "@/components/RoomsList/RoomsList";
import { Spinner } from "@/components/Spinner/Spinner";
import { UserHeader } from "@/components/UserHeader/UserHeader";
import { RoomCreateForm } from "@/components/RoomCreateForm/RoomCreateForm";
import { ModalWrapper } from "@/components/ModalWrapper/ModalWrapper";
import { useModal } from "@/hooks/useModal";

export const RoomsFetchContext = createContext({} as { refetch: () => void });

function MePage() {
    const { content: modal_content, ...modal } = useModal(false);
    const { data: rooms, isLoading, refetch } = useQuery({ queryFn: getMyRooms, queryKey: ["my", "rooms"] });

    return (
        <div className={styles.container}>
            <ModalWrapper {...modal}>{modal_content}</ModalWrapper>

            <UserHeader />

            <div className={styles.rooms_header}>
                <h1>Your rooms</h1>
                <button onClick={() => modal.open(<RoomCreateForm />)}>
                    <AddBoxSVG />
                </button>
            </div>

            <RoomsFetchContext.Provider value={{ refetch: () => refetch() }}>
                {isLoading ? (
                    <Spinner text="Loading" />
                ) : rooms === undefined ? (
                    <p>Failed to fetch rooms</p>
                ) : (
                    <RoomsList rooms={rooms} />
                )}
            </RoomsFetchContext.Provider>
        </div>
    );
}

export default observer(MePage);
