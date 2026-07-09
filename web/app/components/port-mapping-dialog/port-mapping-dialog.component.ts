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
        this.userService.get().subscribe(data => {
            if (data.metadata) {
                this._users = data.data;
            }
        });
    }

    onConfirm(): void {
        let formData = this.form.value as PortMapping;
        formData.user = { "id": formData.user.id, "name": formData.user.name } as User;
        this.dialogRef.close(formData);
    }

    onDismiss(): void {
        this.dialogRef.close(false);
    }
}

