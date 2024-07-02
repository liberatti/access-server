import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { Observable } from 'rxjs';
import { PolicyModel, User } from 'web/app/models/security';
import { APIService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class PolicyService extends APIService<PolicyModel, string> {

    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService
    ) {
        super(httpClient, storageService, "policy");
    }
}