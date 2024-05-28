import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { Observable } from 'rxjs';
import { APIService } from './api.service';
import { PortMappingModel, User } from '../models/security';
import { ServerConfig } from '../models/shared';

@Injectable({
    providedIn: 'root'
})
export class ServerService extends APIService<ServerConfig, string> {
    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService
    ) {
        super(httpClient, storageService, "server");
    }
    getStatus(): Observable<ServerConfig> {
        return this.httpClient.get<ServerConfig>(this.END_POINT + "/status");
    }
    activate(data: ServerConfig): Observable<ServerConfig> {
        return this.httpClient.post<ServerConfig>(this.END_POINT + "/activate", data);
    }
}

@Injectable({
    providedIn: 'root'
})
export class PortMappingService extends APIService<PortMappingModel, string> {
    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService
    ) {
        super(httpClient, storageService, "server/port_map");
    }
}

@Injectable({
    providedIn: 'root'
})
export class UserService extends APIService<User, string> {


    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService
    ) {
        super(httpClient, storageService, "user");
    }

    getConfig(user_id: string): Observable<Blob> {
        return this.httpClient.get<Blob>(this.END_POINT + "/" + user_id + "/config",
            { responseType: 'blob' as 'json' }
        );
    }
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {

    private END_POINT: string;

    constructor(
        protected httpClient: HttpClient,
        protected storageService: LocalStorageService,
    ) {
        let ctx = window.location.pathname as string;
        if (window.location.pathname.length === 1) {
            ctx = "";
        }
        //this.END_POINT = window.location.protocol + "//" + window.location.host + '/admin/api';
        this.END_POINT = "http://localhost:5000/api"

    }

    login(data: User): Observable<any> {
        return this.httpClient.post<any>(this.END_POINT + "/user/login", data);
    }
    logout(): void {
    }

    changeAccount(data: User): Observable<any> {
        return this.httpClient.post<User>(this.END_POINT + "/user/", data);
    }

    getCurrentUser(): Observable<User> {
        return this.httpClient.get<any>(this.END_POINT + "/user/info/");
    }
}