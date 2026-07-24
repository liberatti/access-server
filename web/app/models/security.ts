export interface DMZService{
    id: string;
    name: string;
    description: string;
    port_mappings: Array<PortMapping>;
}



export interface User {
    id: string;
    name: string;
    username: string;
    password: string;
    locale: string;
    session: VPNSession;
    sessions?: Array<VPNSession>;
    policies: Array<AccessPolicy>;
    role:String;
}

export interface PortMapping {
    id: string;
    user: User;
    user_port: number;
    bind_port: number;
    protocol: string;
}

export interface AccessPolicy {
    id: string;
    name: string;
    networks: Array<string>;
    clients: Array<User>;
}

export interface VPNSession {
    id: string;
    remote_port: number;
    remote_ip: string;
    local_ip: string;
    state: string;
}