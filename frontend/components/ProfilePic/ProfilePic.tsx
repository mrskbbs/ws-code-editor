import { stringToColor } from "@/utils";
import styles from "./ProfilePic.module.css";
import PersonSVG from "@/public/svg/person.svg";

interface ICProfilePic extends React.ComponentProps<"span"> {
    id: string;
    username: string;
    is_username_displayed?: boolean;
}

export const ProfilePic = ({ id, username, is_username_displayed, style, ...el }: ICProfilePic) => {
    return (
        <span {...el} className={styles.avatar} style={{ backgroundColor: stringToColor(id), ...style }}>
            <PersonSVG />
            {is_username_displayed === undefined ? <></> : is_username_displayed === false ? <></> : <p>{username}</p>}
        </span>
    );
};
