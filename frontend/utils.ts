export function jsonKey(params: any) {
    return JSON.stringify(params);
}
export function diffCreate(prev: string[], next: string[]): Map<number, string | null> {
    const diffs = new Map<number, string | null>();
    let min_len = prev.length > next.length ? next.length : prev.length;
    for (let i = 0; i < min_len; i++) {
        if (prev[i] !== next[i]) diffs.set(i, next[i]);
    }

    if (prev.length > next.length) {
        for (let i = min_len; i < prev.length; i++) diffs.set(i, null);
    }
    if (prev.length < next.length) {
        for (let i = min_len; i < next.length; i++) diffs.set(i, next[i]);
    }

    return diffs;
}

export function diffApply(arr: string[], diffs: { [key: number]: string | null }) {
    const new_arr = [...arr];
    let max_ind = Math.max(...Object.keys(diffs).map((v) => Number(v)));
    let cut_ind = new_arr.length + 1;

    if (new_arr.length <= max_ind) {
        for (let i = new_arr.length - 1; i < max_ind + 1; i++) {
            new_arr.push("");
        }
    }

    for (let [key, value] of Object.entries(diffs)) {
        let line_ind = Number(key);
        if (value === null) {
            cut_ind = Math.min(cut_ind, line_ind);
            continue;
        }
        new_arr[line_ind] = value;
    }

    if (cut_ind !== new_arr.length + 1) {
        return new_arr.slice(0, cut_ind);
    }

    return new_arr;
}
