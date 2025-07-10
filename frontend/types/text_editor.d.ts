interface IClientSelection extends ISelection {
    cursor: number | null;
}

interface ISelection {
    start: number;
    end: number;
}

type IDirection = "backward" | "forward" | "none";
