import { Injectable, Injector } from '@angular/core';
import { DMZService } from 'web/app/models/security';
import { APIService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class DMZServiceService extends APIService<DMZService, string> {

    constructor(protected override injector: Injector) {
        super(injector, 'dmz')
    }
}