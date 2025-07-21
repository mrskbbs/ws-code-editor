import { createRoom } from "@/api/room";
import { useRouter } from "next/navigation";

export const RoomCreate = () => {
    const router = useRouter();
    return (
        <form
            onSubmit={async (e) => {
                e.preventDefault();
                const form_data = new Map(new FormData(e.currentTarget).entries());
                const payload: any = {};
                for (let [key, value] of form_data.entries()) {
                    if (!value) {
                        console.error("Invalid field");
                        return;
                    }

                    payload[key] = value.toString();
                }
                try {
                    const room_id = await createRoom(payload as IRoomCreateData);
                    router.push(`/rooms/${room_id}`);
                } catch (e) {
                    console.error(e, "failed to create a room");
                }
            }}
        >
            <input id="name" name="name" type="text" />
            <button>Create room</button>
        </form>
    );
};
