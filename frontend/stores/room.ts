import { diffApply } from "@/utils";
import { makeAutoObservable } from "mobx";

export class RoomStore {
    name: string = "";

    code: string[] = [""];
    stdin: string[] = [""];
    stdout: string[] = [];
    stderr: string[] = [];

    connections: IUserData[] = [];
    is_running: boolean = false;

    locations: Map<string, Set<number>> = new Map();

    constructor() {
        makeAutoObservable(this);
    }

    // setCode(diffs: { [key: number]: string | null }) {
    //     this.code = diffApply(this.code, diffs);
    // }

    // setStdin(diffs: { [key: number]: string | null }) {
    //     this.code = diffApply(this.stdin, diffs);
    // }
}
