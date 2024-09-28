import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { UserListComponent } from './view/user-list/user-list.component';
import { SiginComponent } from './view/sign-in/sign-in.component';
import { PublicLayoutComponent } from './layouts/public-layout/public-layout.component';
import { UserFormComponent } from './view/user-form/user-form.component';
import { PolicyListComponent } from './view/policy-list/policy-list.component';
import { PolicyFormComponent } from './view/policy-form/policy-form.component';
import { WizardComponent } from './view/wizard/wizard.component';
import { DmzServiceListComponent } from './view/dmz-service-list/dmz-service-list.component';
import { DMZServiceFormComponent } from './view/dmz-service-form/dmz-service-form.component';

export const routes: Routes = [
    {
        path: 'wizard',
        component: PublicLayoutComponent,
        children: [
            { path: '', component: WizardComponent },
        ]
    },
    {
        path: 'login',
        component: PublicLayoutComponent,
        children: [
            { path: '', component: SiginComponent },
        ]
    },
    {
        path: 'user',
        component: AdminLayoutComponent,
        children: [
            { path: '', component: UserListComponent },
            { path: 'add', component: UserFormComponent },
            { path: 'edit/:id', component: UserFormComponent },
        ]
    },
    {
        path: 'dmz',
        component: AdminLayoutComponent,
        children: [
            { path: '', component: DmzServiceListComponent },
            { path: 'add', component: DMZServiceFormComponent },
            { path: 'edit/:id', component: DMZServiceFormComponent },
        ]
    },
    {
        path: 'policy',
        component: AdminLayoutComponent,
        children: [
            { path: '', component: PolicyListComponent },
            { path: 'add', component: PolicyFormComponent },
            { path: 'edit/:id', component: PolicyFormComponent },
        ]
    },
    {
        path: '**',
        redirectTo: 'wizard',
        pathMatch: 'full'
    }
];