import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { UserListComponent } from './view/user-list/user-list.component';
import { SiginComponent } from './view/sigin/sigin.component';
import { AuthLayoutComponent } from './layouts/auth-layout/auth-layout.component';
import { UserFormComponent } from './view/user-form/user-form.component';
import { PolicyListComponent } from './view/policy-list/policy-list.component';
import { PolicyFormComponent } from './view/policy-form/policy-form.component';
import { WizardComponent } from './view/wizard/wizard.component';

export const routes: Routes = [
    {
        path: 'wizard',
        component: AuthLayoutComponent,
        children: [
            { path: '', component: WizardComponent },
        ]
    },
    {
        path: 'login',
        component: AuthLayoutComponent,
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