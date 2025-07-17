import { diffApply } from "@/utils";
import { makeAutoObservable } from "mobx";

export class RoomStore {
    name: string = "";
    invite_token: string = "";

    code: string[] = [""];
    stdin: string[] = [""];
    stdout: string[] = [];
    stderr: string[] = [];

    connections: IUserData[] = [];
    is_running: boolean = false;

    locations_code: Map<string, Set<number>> = new Map();
    locations_stdin: Map<string, Set<number>> = new Map();

    constructor() {
        makeAutoObservable(this);
    }

    setCode(val: string[]) {
        this.code = val;
    }

    setStdin(val: string[]) {
        this.code = val;
    }

    setLocationsCode(val: Map<string, Set<number>>) {
        this.locations_code = val;
    }

    setLocationsStdin(val: Map<string, Set<number>>) {
        this.locations_stdin = val;
    }
}
