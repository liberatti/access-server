import { Inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { PolicyModel } from 'web/app/models/security';
import { APIService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class PolicyService extends APIService<PolicyModel, string> {

    constructor(
        httpClient: HttpClient,
        storageService: LocalStorageService,
        @Inject('REST_API_URL') REST_API_URL: string
    ) {
        super(httpClient, storageService, `${REST_API_URL}/policy`);
    }
}