import { getMyself, login, logout, signup } from "@/api/auth";
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

    async signup(data: ISignupData) {
        await signup(data);
        this.update();
    }

    async login(data: ILoginData) {
        await login(data);
        this.update();
    }

    async logout() {
        await logout();
        this.update();
    }
}

export const auth_store = new AuthStore();
