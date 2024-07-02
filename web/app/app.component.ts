import { Component, OnInit } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { Router, RouterOutlet } from '@angular/router';
import { LoadingService } from './services/loading.service';
import { LocalStorageService } from './services/localstorage.service';
import { AuthService, PortMappingService, ServerService, UserService } from './services/security.service';
import { NotificationService } from './services/notification.service';
import { FilterByPropertyPipe } from './pipes/filter_by_property.pipe';
import { PolicyService } from 'web/app/services/policy.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: '<router-outlet></router-outlet>',
  providers: [
    { provide: LocationStrategy, useClass: HashLocationStrategy },
    { provide: 'LOCALSTORAGE', useValue: window.localStorage },
    AuthService, UserService, PolicyService, NotificationService, LocalStorageService,
    LoadingService, FilterByPropertyPipe, PortMappingService, ServerService
  ],
})
export class AppComponent {



}