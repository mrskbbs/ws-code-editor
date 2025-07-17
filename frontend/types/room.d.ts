interface IRoom {
    id: string;
    name: string;
    users: IUserData[];
    creator: IUserData;
    created_at: number;
}
interface IRoomCreateData {
    name: string;
}
