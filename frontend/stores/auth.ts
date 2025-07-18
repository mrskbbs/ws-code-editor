import { getMyself, login, signup } from "@/api/auth";
import { makeAutoObservable } from "mobx";

class AuthStore {
    user: IUserData | null = null;

    constructor() {
        this.user = null;
        makeAutoObservable(this);
    }

    update() {
        getMyself()
            .then((new_user) => (this.user = new_user))
            .catch((err) => {
                console.error("Failed to get user credentials");
                this.user = null;
            });
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
