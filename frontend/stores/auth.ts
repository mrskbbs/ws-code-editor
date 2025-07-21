import { getMyself, login, signup } from "@/api/auth";
import { computed, makeAutoObservable } from "mobx";

class AuthStore {
    user: IUserData | null = null;

    constructor() {
        this.user = null;
        makeAutoObservable(this);
    }

    async update() {
        this.user = await getMyself();
    }

    signup(data: ISignupData) {
        signup(data)
            .then(() => {
                this.update();
            })
            .catch((err) => {
                console.log("Failed to signup");
            });
    }

    login(data: ILoginData) {
        login(data)
            .then(() => {
                this.update();
            })
            .catch((err) => {
                console.log("Failed to signup");
            });
    }
}

export const auth_store = new AuthStore();
