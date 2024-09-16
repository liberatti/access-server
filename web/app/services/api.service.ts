import { HttpClient, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { APIOperations, Page, PageMeta } from '../models/shared';
import { LocalStorageService } from './localstorage.service';

@Injectable({
    providedIn: 'root'
})
export abstract class APIService<T, ID> implements APIOperations<T, ID> {
    protected readonly END_POINT: string;

    constructor(
        protected httpClient: HttpClient,
        protected storageService: LocalStorageService,
        protected P_END_POINT: string
    ) {
        this.END_POINT = P_END_POINT;
    }

    get(pagging?: PageMeta): Observable<Page> {
        let params = new HttpParams();
        if (pagging) {
            params = params.append('page', pagging.page);
            params = params.append('size', pagging.per_page);
        }
        return this.httpClient.get<Page>(this.END_POINT, { params: params });
    }

    getById(id: ID): Observable<T> {
        return this.httpClient.get<T>(this.END_POINT + "/" + id);
    }

    getByName(name: string, pagging?: PageMeta): Observable<Page> {
        let options = {
            params: new HttpParams()
        }
        options.params = options.params.append("name", name);
        if (pagging) {
            options.params = options.params.append("page", pagging.page);
            options.params = options.params.append("size", pagging.per_page);
        }
        return this.httpClient.get<Page>(this.END_POINT, options);
    }

    removeById(id: ID): Observable<T> {
        return this.httpClient.delete<T>(this.END_POINT + "/" + id);
    }

    save(data: Partial<T>): Observable<T> {
        return this.httpClient.post<T>(this.END_POINT, data);
    }
    update(id: ID, data: T): Observable<T> {
        return this.httpClient.put<T>(this.END_POINT + "/" + id, data);
    }

    protected initHeaders(): Headers {
        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        let token = "USER_TOKEN";
        if (token !== null) {
            headers.append('Authorization', token);
        }

        headers.append('Pragma', 'no-cache');
        headers.append('Content-Type', 'application/json');
        headers.append('Access-Control-Allow-Origin', '*');
        return headers;
    }
}