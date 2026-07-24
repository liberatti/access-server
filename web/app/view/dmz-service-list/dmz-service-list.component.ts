import { AfterViewInit, Component, OnInit } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MatMomentDateModule } from '@angular/material-moment-adapter';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSortModule } from '@angular/material/sort';
import { MatStepperModule } from '@angular/material/stepper';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ConfirmDialogComponent } from 'web/app/components/confirm-dialog/confirm-dialog.component';
import { DMZService } from 'web/app/models/security';
import { DefaultPageMeta } from 'web/app/models/shared';
import { NotificationService } from 'web/app/services/notification.service';
import { FileSaverModule } from 'ngx-filesaver';
import { DMZServiceService } from 'web/app/services/dmz.service';

@Component({
    selector: 'app-dmz-service-list',
    templateUrl: './dmz-service-list.component.html',
    standalone: true,
    imports: [RouterModule,
        ReactiveFormsModule, TranslateModule, FileSaverModule,
        MatAutocompleteModule, MatMomentDateModule, MatCheckboxModule,
        MatSidenavModule, MatIconModule, MatButtonModule,
        MatListModule, MatCardModule, MatProgressBarModule, MatInputModule,
        MatTableModule, MatBadgeModule, MatMenuModule, MatSortModule,
        MatTooltipModule, MatSelectModule, MatPaginatorModule, MatChipsModule,
        MatStepperModule, MatRadioModule, MatFormFieldModule, MatGridListModule
    ],
})
export class DmzServiceListComponent implements OnInit, AfterViewInit {
    dmzDC: string[] = ['name', 'port_mappings', 'action'];
    dmzDS: MatTableDataSource<DMZService>;
    dmzPA = new DefaultPageMeta();

    constructor(
        private notificationService: NotificationService,
        private dmzService: DMZServiceService,
        private confirmDialog: MatDialog
    ) {
        this.dmzDS = new MatTableDataSource<DMZService>();
    }

    ngOnInit(): void {
        this.updateGridTable();
    }

    ngAfterViewInit() {
    }

    updateGridTable() {
        this.dmzService.get(this.dmzPA).subscribe((res: any) => {
            if (res.metadata) {
                this.dmzPA.total_elements = res.metadata.total_elements || 0;
                this.dmzDS.data = res.data;
            } else {
                this.dmzDS.data = [];
                this.dmzPA.total_elements = 0;
            }
        });
    }

    nextPage(event: any) {
        this.dmzPA.page = event.pageIndex + 1;
        this.dmzPA.per_page = event.pageSize;
        this.updateGridTable();
    }

    onSave() {
        this.updateGridTable();
    }

    onRemove(dto: DMZService) {
        const dialogRef = this.confirmDialog.open(ConfirmDialogComponent, {
            data: { title: "Confirm service removal ", message: "Remove " + dto.name },
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result && dto.id) {
                this.dmzService.removeById(dto.id).subscribe(() => {
                    this.updateGridTable();
                    this.notificationService.openSnackBar('Service removed');
                });
            }
        });
    }
}
