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

export function diffApply(arr: string[], diffs_obj: { [key: number]: string | null }) {
    const diffs = new Map<number, string | null>();
    for (let [key, value] of Object.entries(diffs_obj)) {
        diffs.set(Number(key), value);
    }

    let diffs_len = Math.max(...diffs.keys()) + 1;
    let new_arr: string[] = [...arr];

    if (new_arr.length < diffs_len) {
        for (let i = new_arr.length - 1; i < diffs_len; i++) {
            new_arr.push("");
        }
    }

    let cut_ind = new_arr.length + 1;

    for (let [ind, val] of diffs) {
        if (val === null) {
            cut_ind = Math.min(cut_ind, ind);
        } else {
            new_arr[ind] = val;
        }
    }
    console.log(new_arr.slice(0, cut_ind));
    return new_arr.slice(0, cut_ind);
    // for (let [key, value] of Object.entries(diffs_obj)) {
    //     diffs.set(Number(key), value);
    // }

    // const new_arr: string[] = [...arr];
    // let max_ind = Math.max(...Object.keys(diffs).map((v) => Number(v)));

    // if (new_arr.length <= max_ind) {
    //     for (let i = new_arr.length - 1; i < max_ind + 1; i++) {
    //         new_arr.push("");
    //     }
    // }
    // let cut_ind = new_arr.length + 1;

    // for (let [line_ind, value] of diffs) {
    //     if (value === null) {
    //         cut_ind = Math.min(cut_ind, line_ind);
    //     } else {
    //         new_arr[line_ind] = value as string;
    //     }
    // }
    // console.log(new_arr, cut_ind);
    // if (cut_ind !== new_arr.length + 1) {
    //     return new_arr.slice(0, cut_ind);
    // }

    // return new_arr as string[];
}
