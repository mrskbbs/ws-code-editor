import { memo } from "react";
import { Room } from "./Room/Room";
import styles from "./RoomsList.module.css";

interface ICRoomsList {
    rooms: IRoom[];
}

export const RoomsList = ({ rooms }: ICRoomsList) => {
    return (
        <div className={styles.rooms}>
            {rooms.map((room) => (
                <Room key={room.id} room={room} />
            ))}
        </div>
    );
};
