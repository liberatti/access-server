import { Injectable, NgZone, inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptor } from '@angular/common/http';
import { HttpRequest } from '@angular/common/http';
import { HttpHandler } from '@angular/common/http';
import { HttpEvent } from '@angular/common/http';
import { AuthService } from 'web/app/services/security.service';
import { LocalStorageService } from '../services/localstorage.service';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from "rxjs/operators";


import { HttpInterceptorFn } from '@angular/common/http';

export const JwtInterceptor: HttpInterceptorFn = (req, next) => {
    const storageService = inject(LocalStorageService);
    const ngZone = inject(NgZone);
    const router = inject(Router);
    
    let auth = storageService.get('x-auth');
    let authReq = req;
    if (auth) {
        authReq = req.clone({
            setHeaders: { Authorization: auth.token_type + ' ' + auth.access_token }
        });
    }

    return next(authReq).pipe(
        catchError((err: any) => {
            
            if (err instanceof HttpErrorResponse) {
                if (err.status === 401) {
                    ngZone.run(() => {
                        router.navigateByUrl('/login');
                    });
                } else {
                    console.error('HTTP error:', err);
                }
            } else {
                console.error('An error occurred:', err);
            }
            return throwError(() => err);
        })
    );;
};