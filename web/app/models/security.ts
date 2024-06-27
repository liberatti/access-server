
export interface User {
    id: string;
    name: string;
    username: string;
    password: string;
    locale: string;
    policies: Array<PolicyModel>;
    port_mappings: Array<PortMappingModel>;
    sessions: Array<VPNSession>;

}
export interface PortMappingModel {
    id: string;
    user_port: number;
    bind_port: number;
    protocol: string;
    type: string;
}

export interface PolicyModel {
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