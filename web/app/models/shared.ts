import { Observable } from "rxjs";

export interface APIOperations<T, ID> {
    get(pagging?: PageMeta): Observable<Page>;
    getById(id: ID): Observable<T>;
    getByName(name: string, pagging?: PageMeta): Observable<Page>;
    removeById(id: ID): Observable<T>;
    save(data: Partial<T>): Observable<T>;
    update(id: ID, data: T): Observable<T>;
}

export interface FrontendConfig {
    locale: any;
    navGroup: string;
    navResource: string;
    screenSize: string;
    sidenavOpened: boolean;
    formats: any;
}

export interface Language {
    id: string;
    name: string;
}

export interface PageMeta {
    total_elements: number;
    total_pages: number;
    per_page: number;
    page: number;
}

export interface Page {
    data: [],
    metadata: PageMeta,
}

export class DefaultPageMeta implements PageMeta {
    page: number = 1;
    per_page: number = 10;
    total_elements: number = 0;
    total_pages: number = 1;
}

export interface ServerConfig {
    name: string;
    subnet: string;
    public_address: string;
    public_port: number;
    admin_user: string;
    admin_pass: string;
    status: string;
}