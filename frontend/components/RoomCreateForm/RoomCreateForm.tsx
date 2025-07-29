import { createRoom } from "@/api/room";
import { useRouter } from "next/navigation";
import { useContext } from "react";
import { ModalWrapperContext } from "../ModalWrapper/ModalWrapper";
import { ErrorDisplay } from "../ErrorDisplay/ErrorDisplay";

export const RoomCreateForm = () => {
    const router = useRouter();
    const { open } = useContext(ModalWrapperContext);
    return (
        <form
            onSubmit={async (e) => {
                e.preventDefault();
                const form_data = new Map(new FormData(e.currentTarget).entries());
                const payload: any = {};
                try {
                    for (let [key, value] of form_data.entries()) {
                        if (!value) {
                            throw Error("Invalid field");
                        }

                        payload[key] = value.toString();
                    }
                    const room_id = await createRoom(payload as IRoomCreateData);
                    router.push(`/rooms/${room_id}`);
                } catch (err) {
                    if (err instanceof Error) open(<ErrorDisplay err={err} />);
                }
            }}
        >
            <label htmlFor="name">Name</label>
            <input id="name" name="name" type="text" />
            <button className={`beauty_button`}>Create room</button>
        </form>
    );
};
