import { Injectable, Injector } from '@angular/core';
import { Observable } from 'rxjs';
import { APIService } from './api.service';
import { PortMapping, User } from '../models/security';
import { ServerConfig } from '../models/shared';

@Injectable({
    providedIn: 'root'
})
export class ServerService extends APIService<ServerConfig, string> {
    constructor(protected override injector: Injector) {
        super(injector, 'server')
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
export class PortMappingService extends APIService<PortMapping, string> {
    constructor(protected override injector: Injector) {
        super(injector, 'server/port_map')
    }
}

@Injectable({
    providedIn: 'root'
})
export class UserService extends APIService<User, string> {

    constructor(protected override injector: Injector) {
        super(injector, 'user')
    }

    getConfig(user_id: string, target: string): Observable<Blob> {
        return this.httpClient.get<Blob>(this.END_POINT + "/" + user_id + "/config/" + target,
            { responseType: 'blob' as 'json' }
        );
    }
}

@Injectable({
    providedIn: 'root'
})
export class AuthService extends APIService<User, string> {

    constructor(protected override injector: Injector) {
        super(injector, 'user')
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