import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MatDialogActions, MatDialogContent, MatDialogTitle } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { environment } from 'web/environments/environment';

@Component({
    selector: 'app-about-dialog',
    templateUrl: './about-dialog.component.html',
    standalone: true,
    imports: [
        MatButtonModule,
        MatIconModule,
        MatDialogTitle,
        MatDialogContent,
        MatDialogActions,
        TranslateModule
    ],
})

export class AboutDialogComponent {
    version = environment.version;

    constructor(
        public dialogRef: MatDialogRef<AboutDialogComponent>
    ) { }

    onDismiss(): void {
        this.dialogRef.close();
    }
}