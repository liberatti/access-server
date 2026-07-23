import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatOptionModule } from '@angular/material/core';
import { MatDialogRef, MatDialogActions, MatDialogClose, MatDialogContent, MatDialogTitle } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { PortMapping, User } from 'web/app/models/security';
import { PortMappingService, UserService } from 'web/app/services/security.service';

@Component({
    selector: 'app-port-mapping-dialog',
    templateUrl: './port-mapping-dialog.component.html',
    standalone: true,
    imports: [ReactiveFormsModule,
        MatFormFieldModule, CommonModule,
        MatInputModule,
        FormsModule, MatCardModule,
        MatButtonModule,
        MatDialogTitle,
        MatDialogContent,
        MatDialogActions,
        MatSelectModule
    ],
})

export class PortMappingDialogComponent implements OnInit {
    _users: Array<User> = [];
    _supportedProtocols = ['ICMP', 'TCP', 'UDP'];

    form = new FormGroup({
        user: new FormControl<User>({} as User),
        user_port: new FormControl<number>(8080),
        bind_port: new FormControl<number>(8080),
        protocol: new FormControl<string>('TCP')
    });

    constructor(
        public dialogRef: MatDialogRef<PortMappingDialogComponent>,
        private portService: PortMappingService,
        private userService: UserService
    ) { }
    ngOnInit(): void {
        this.userService.get().subscribe((res: any) => {
            if (res && res.data) {
                this._users = res.data;
            } else if (Array.isArray(res)) {
                this._users = res;
            }
        });
    }

    onConfirm(): void {
        const val = this.form.value as any;
        const userObj = val.user;
        const userId = userObj?.id || userObj?._id || 'user_' + Date.now();
        const userName = userObj?.name || userObj?.username || 'User';

        const portMapping: PortMapping = {
            id: userId,
            user: { id: userId, name: userName, username: userName } as User,
            user_port: Number(val.user_port || 8080),
            bind_port: Number(val.bind_port || 8080),
            protocol: val.protocol || 'TCP'
        } as PortMapping;

        this.dialogRef.close(portMapping);
    }

    onDismiss(): void {
        this.dialogRef.close(false);
    }
}

