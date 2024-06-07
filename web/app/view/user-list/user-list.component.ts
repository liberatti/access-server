import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
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
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
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
import { User } from 'web/app/models/security';
import { DefaultPageMeta } from 'web/app/models/shared';
import { NotificationService } from 'web/app/services/notification.service';
import { UserService } from 'web/app/services/security.service';
import { FileSaverModule, FileSaverService } from 'ngx-filesaver';

@Component({
    selector: 'app-user-list',
    templateUrl: './user-list.component.html',
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
export class UserListComponent implements OnInit, AfterViewInit {
    userDC: string[] = ['name', 'extra_networks', 'role', 'action'];
    userDS: MatTableDataSource<never>;
    userPA = new DefaultPageMeta();

    constructor(
        private notificationService: NotificationService,
        private userService: UserService,
        private confirmDialog: MatDialog,
        private fileSaver: FileSaverService
    ) {
        this.userDS = new MatTableDataSource<never>;

    }

    ngOnInit(): void {
        this.updateGridTable();
    }
    ngAfterViewInit() {
    }
    updateGridTable() {
        this.userService.get(this.userPA).subscribe(data => {
            this.userDS = new MatTableDataSource(data.data);
            this.userPA.total_elements = data.metadata.total_elements;
        });
    }

    nextPage(event: any) {
        this.userPA.page = event.pageIndex + 1;
        this.userPA.per_page = event.pageSize;
        this.updateGridTable();
    }


    donwloadConfig(user_id: string) {
        this.userService.getConfig(user_id).subscribe(data => {
            this.fileSaver.save(data, "client.ovpn");
        });
    }
    onSave() {
        this.userService.get(this.userPA).subscribe(data => {
            this.userDS = new MatTableDataSource(data.data);
            this.userPA.total_elements = data.metadata.total_elements;
        });
        console.log("onSave");
    }
    onRemove(dto: User) {
        const dialogRef = this.confirmDialog.open(ConfirmDialogComponent, {
            data: { title: "Confirm user removal ", message: "Remove " + dto.name },
        });

        dialogRef.afterClosed().subscribe(result => {
            // accepted
            if (result && dto.id) {
                this.userService.removeById(dto.id).subscribe(data => {
                    this.updateGridTable();
                    this.notificationService.openSnackBar('User removed');
                });
            }
        });
    }

}
