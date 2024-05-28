
export interface User {
    id: string;
    name: string;
    username: string;
    password: string;
    locale: string;
    policies: Array<PolicyModel>;
    port_mappings: Array<PortMappingModel>;
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