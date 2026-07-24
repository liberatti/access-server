import { Injectable, Injector } from '@angular/core';
import { AccessPolicy } from 'web/app/models/security';
import { APIService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class PolicyService extends APIService<AccessPolicy, string> {

    constructor(protected override injector: Injector) {
        super(injector, 'policy')
    }
}