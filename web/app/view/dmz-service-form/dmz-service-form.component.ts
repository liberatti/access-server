import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormsModule, FormControl, FormGroup, AbstractControl } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatOptionModule } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AccessPolicy, DMZService, PortMapping, User } from 'web/app/models/security';
import { FilterByPropertyPipe } from 'web/app/pipes/filter_by_property.pipe';
import { NotificationService } from 'web/app/services/notification.service';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { PortMappingDialogComponent } from 'web/app/components/port-mapping-dialog/port-mapping-dialog.component';
import { DMZServiceService } from 'web/app/services/dmz.service';

@Component({
  selector: 'app-dmz-service-form',
  standalone: true,
  imports: [ReactiveFormsModule, TranslateModule, CommonModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule, MatCardModule,
    MatButtonModule, MatIcon, MatChipsModule,
    RouterModule, MatTooltipModule, MatSelectModule, MatOptionModule,
    MatIconModule, MatButtonModule, MatSlideToggleModule
  ],
  templateUrl: './dmz-service-form.component.html'
})
export class DMZServiceFormComponent implements OnInit {
  isAddMode: boolean;
  submitted = false;
  _policies: Array<AccessPolicy> = [];
  isAdmin: boolean = false;
  form = new FormGroup({
    id: new FormControl<string>(''),
    name: new FormControl<string>(''),
    description: new FormControl<string>(''),
    port_mappings: new FormControl<Array<PortMapping>>([]),
  });
  policyForm = new FormGroup({
    policy: new FormControl<AccessPolicy>({} as AccessPolicy)
  });

  constructor(
    private notificationService: NotificationService,
    private route: ActivatedRoute,
    private router: Router,
    private dmzService: DMZServiceService,
    private portDialog: MatDialog
  ) {
    this.isAddMode = false;
  }

  ngOnInit(): void {
    this.isAddMode = !this.route.snapshot.params['id'];

    if (!this.isAddMode) {
      this.dmzService.getById(this.route.snapshot.params['id']).subscribe(data => {
        this.form.get('id')?.setValue(data.id);
        this.form.get('name')?.setValue(data.name);
        this.form.get('description')?.setValue(data.description);
        this.form.get('port_mappings')?.setValue(data.port_mappings);
      });
    }
  }
  onSubmit() {
    this.submitted = true;
    if (this.form.status === "INVALID") {
      return;
    }
    const formData = this.form.value as DMZService;
    if (this.isAddMode) {
      Reflect.deleteProperty(formData, 'id');
      this.dmzService.save(formData).subscribe(() => {
        this.notificationService.openSnackBar('DMZ saved');
        this.router.navigate(['/dmz']);
      });
    } else {
      this.dmzService.update(formData.id, formData).subscribe(() => {
        this.notificationService.openSnackBar('DMZ updated');
        this.router.navigate(['/dmz']);
      });
    }
  }

  onAddPort(): void {
    const dialogRef = this.portDialog.open(PortMappingDialogComponent, {
      width: '450px'
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const current = (this.form.get('port_mappings')?.value || []) as Array<PortMapping>;
        const updated = [...current, result];
        this.form.get('port_mappings')?.setValue(updated);
        this.form.markAsDirty();
      }
    });
  }

  onRemovePort(keyword: any): void {
    const current = (this.form.get('port_mappings')?.value || []) as Array<PortMapping>;
    const updated = current.filter(port => port.id !== keyword && port.user?.id !== keyword);
    this.form.get('port_mappings')?.setValue(updated);
    this.form.markAsDirty();
  }

  compareFn(object1: any, object2: any) {
    return object1 && object2 && object1.id === object2.id;
  }
  get f(): { [key: string]: AbstractControl } {
    return this.form.controls;
  }
}
