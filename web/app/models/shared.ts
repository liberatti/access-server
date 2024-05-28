import { Observable } from "rxjs";

export interface APIOperations<T, ID> {
    get(pagging?: Pageable): Observable<Page>;
    getById(id: ID): Observable<T>;
    getByName(name: string, pagging?: Pageable): Observable<Page>;
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
export interface Pageable {
    offset: number,
    page: number,
    per_page: number,
}

export interface Page {
    content: [],
    pageable: Pageable,
    last: boolean,
    total_pages: number,
    total_elements: number,
    size: number,
    number: number,
    first: boolean,
    empty: boolean
}

export class DefaultPageable implements Pageable {
    offset: number = 0
    paged: boolean = true
    unpaged: boolean = false
    page: number = 1;
    per_page: number = 10;
    total_elements: number = 0;
}

export interface ServerConfig {
    name:string;
    subnet:string;
    public_address:string;
    public_port:number;
    admin_user:string;
    admin_pass:string;
    status:string;
}