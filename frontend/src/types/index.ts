export interface Item {
    name: string;
    size: string;
    position: string;
    fragile: boolean;
}

export interface Action {
    description: string;
    type: string;
}

export interface Task {
    description: string;
    type: string;
    actions: Action[];
}

export interface Plan {
    tasks: Task[];
}