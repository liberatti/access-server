import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogRef, MatDialogActions, MatDialogClose, MatDialogContent, MatDialogTitle } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { PortMappingModel } from 'web/app/models/security';
import { PortMappingService } from 'web/app/services/security.service';

@Component({
    selector: 'app-port-mapping-dialog',
    templateUrl: './port-mapping-dialog.component.html',
    standalone: true,
    imports: [ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        FormsModule, MatCardModule,
        MatButtonModule,
        MatDialogTitle,
        MatDialogContent,
        MatDialogActions,
        MatDialogClose,
    ],
})

export class PortMappingDialogComponent implements OnInit {
    form = new FormGroup({
        user_port: new FormControl<number>(0),
        bind_port: new FormControl<number>(0),
        protocol: new FormControl<string>('tcp'),
        type: new FormControl<string>('static'),
    });

    constructor(
        public dialogRef: MatDialogRef<PortMappingDialogComponent>,
        private portService: PortMappingService
    ) {

    }
    ngOnInit(): void {
        
    }

    onConfirm(): void {
        let formData = this.form.value as PortMappingModel;
        this.portService.save(formData).subscribe({
            next: (result) => {
                formData.id = result.id;
                this.dialogRef.close(formData);
            }, error: (error) => {
                console.error('Erro no subscribe', error);
            }
        });
    }

    onDismiss(): void {
        this.dialogRef.close(false);
    }
}

