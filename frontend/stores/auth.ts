import { getMyself } from "@/api/auth";
import { makeAutoObservable } from "mobx";

class AuthStore {
    user: IUserData | null = null;

    constructor() {
        this.user = null;
        makeAutoObservable(this);
    }

    async update() {
        getMyself()
            .then((new_user) => (this.user = new_user))
            .catch((err) => {
                console.error("Failed to get user credentials");
                this.user = null;
            });
    }
}

export const auth_store = new AuthStore();
