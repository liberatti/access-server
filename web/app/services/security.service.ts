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
export class AuthService extends APIService<User, string> {

    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService
    ) {
        super(httpClient, storageService, "user");
    }

    login(data: User): Observable<any> {
        return this.httpClient.post<any>(this.END_POINT + "/login", data);
    }
    logout(): void {
    }

    changeAccount(data: User): Observable<any> {
        return this.httpClient.post<User>(this.END_POINT + "/", data);
    }

    getCurrentUser(): Observable<User> {
        return this.httpClient.get<any>(this.END_POINT + "/info/");
    }
}