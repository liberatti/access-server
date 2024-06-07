import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
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
import { User } from 'web/app/models/security';
import { DefaultPageMeta } from 'web/app/models/shared';
import { NotificationService } from 'web/app/services/notification.service';
import { PolicyService } from 'web/app/services/policy.service';

@Component({
  selector: 'app-policy-list',
  standalone: true,
  imports: [RouterModule,CommonModule,
    ReactiveFormsModule, TranslateModule,
    MatAutocompleteModule, MatMomentDateModule, MatCheckboxModule,
    MatSidenavModule, MatIconModule, MatButtonModule,
    MatListModule, MatCardModule, MatProgressBarModule, MatInputModule,
    MatTableModule, MatBadgeModule, MatMenuModule, MatSortModule,
    MatTooltipModule, MatSelectModule, MatPaginatorModule, MatChipsModule,
    MatStepperModule, MatRadioModule, MatFormFieldModule, MatGridListModule
  ],
  templateUrl: './policy-list.component.html'
})
export class PolicyListComponent {
  displayedColumns: string[] = ['name', 'networks', 'total_targets', 'action'];

  dataSource: MatTableDataSource<never>;
  policyPA = new DefaultPageMeta();

  constructor(
    private notificationService: NotificationService,
    private policyService: PolicyService,
    private confirmDialog: MatDialog
  ) {
    this.dataSource = new MatTableDataSource<never>;

  }

  ngOnInit(): void {
    this.updateGridTable();
  }

  updateGridTable() {
    this.policyService.get(this.policyPA).subscribe(data => {
      this.dataSource = new MatTableDataSource(data.data);
      this.policyPA.total_elements = data.metadata.total_elements;
    });
  }

  nextPage(event: any) {
    this.policyPA.page = event.pageIndex + 1;
    this.policyPA.per_page = event.pageSize;
    this.updateGridTable();
  }

  onSave() {
    this.policyService.get(this.policyPA).subscribe(data => {
      this.dataSource = new MatTableDataSource(data.data);
      this.policyPA.total_elements = data.metadata.total_elements;
    });
    console.log("onSave");
  }
  onRemove(dto: User) {
    const dialogRef = this.confirmDialog.open(ConfirmDialogComponent, {
      data: { title: "Confirm policy removal ", message: "Remove " + dto.name },
    });

    dialogRef.afterClosed().subscribe(result => {
      // accepted
      if (result && dto.id) {
        this.policyService.removeById(dto.id).subscribe(data => {
          this.updateGridTable();
          this.notificationService.openSnackBar('User removed');
        });
      }
    });
  }
}
