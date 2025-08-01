import { auth_store } from "@/stores/auth";
import { observer } from "mobx-react-lite";
import { useRouter } from "next/navigation";
import { ProfilePic } from "../ProfilePic/ProfilePic";
import styles from "./UserHeader.module.css";
import LeaveSVG from "@/public/svg/leave.svg";

export const UserHeader = observer(() => {
    const router = useRouter();

    // I dont want to use ? for every auth_store usage
    if (auth_store.user === null) return;

    return (
        <div className={styles.user_header}>
            <ProfilePic id={auth_store.user.id} username={auth_store.user.username} style={{ gridArea: "av" }} />
            <h2 style={{ gridArea: "un" }}>{auth_store.user.username}</h2>
            <p className={styles.user_id} style={{ gridArea: "id" }}>
                {auth_store.user.id}
            </p>
            <button
                className={styles.logout}
                onClick={() => {
                    auth_store
                        .logout()
                        .finally(() => router.push("/"))
                        .catch((err) => console.error(err.message));
                }}
            >
                <LeaveSVG />
            </button>
        </div>
    );
});
