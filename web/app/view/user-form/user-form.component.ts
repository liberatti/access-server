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
import { PortMappingDialogComponent } from 'web/app/components/port-mapping-dialog/port-mapping-dialog.component';
import { PolicyModel, PortMappingModel, User } from 'web/app/models/security';
import { FilterByPropertyPipe } from 'web/app/pipes/filter_by_property.pipe';
import { NotificationService } from 'web/app/services/notification.service';
import { PolicyService } from 'web/app/services/policy.service';
import { PortMappingService, UserService } from 'web/app/services/security.service';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [ReactiveFormsModule, TranslateModule, CommonModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule, MatCardModule,
    MatButtonModule, MatIcon, MatChipsModule,
    RouterModule, MatTooltipModule, MatSelectModule, MatOptionModule,
    MatIconModule, MatButtonModule, FilterByPropertyPipe
  ],
  templateUrl: './user-form.component.html'
})
export class UserFormComponent implements OnInit {
  isAddMode: boolean;
  submitted = false;
  _policies: Array<PolicyModel> = [];

  form = new FormGroup({
    id: new FormControl<string>(''),
    name: new FormControl<string>(''),
    username: new FormControl<string>(''),
    password: new FormControl<string>(''),
    port_mappings: new FormControl<Array<PortMappingModel>>([]),
    policies: new FormControl<Array<PolicyModel>>([])
  });
  policyForm = new FormGroup({
    policy: new FormControl<PolicyModel>({} as PolicyModel)
  });

  constructor(
    private notificationService: NotificationService,
    private route: ActivatedRoute,
    private router: Router,
    private policyService: PolicyService,
    private userService: UserService,
    private portDialog: MatDialog,
    private portService: PortMappingService


  ) {
    this.isAddMode = false;
  }

  ngOnInit(): void {
    this.isAddMode = !this.route.snapshot.params['id'];

    this.policyService.get().subscribe(data => {
      this._policies = data.content;
    });

    if (!this.isAddMode) {
      this.userService.getById(this.route.snapshot.params['id']).subscribe(data => {
        this.form.get('id')?.setValue(data.id);
        this.form.get('name')?.setValue(data.name);
        this.form.get('username')?.setValue(data.username);
        this.form.get('port_mappings')?.setValue(data.port_mappings);
        this.form.get('policies')?.setValue(data.policies);
      });
    }
  }
  onSubmit() {
    this.submitted = true;
    if (this.form.status === "INVALID") {
      return;
    }
    const formData = this.form.value as User;
    if (this.isAddMode) {
      Reflect.deleteProperty(formData, 'id');
      console.log(formData);
      this.userService.save(formData).subscribe(() => {
        this.notificationService.openSnackBar('Policy saved');
        this.router.navigate(['/user']);
      });
    } else {
      this.userService.update(formData.id, formData).subscribe(() => {
        this.notificationService.openSnackBar('Policy updated');
        this.router.navigate(['/user']);
      });
    }
  }

  onAddPolicy(): void {
    let data = this.policyForm.value.policy as PolicyModel;
    if (this.form.value.policies != null) {
      this.form.value.policies.push(data);
    }
    this.policyForm.reset();
  }
  onRemovePolicy(keyword: any): void {
    if (this.form.value.policies != null) {
      this.form.value.policies = this.form.value.policies.filter(policy => policy.id !== keyword);
    }
  }

  onAddPort(): void {
    const dialogRef = this.portDialog.open(PortMappingDialogComponent, {
      width: '450px'
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        let arr = this.form.value.port_mappings as Array<PortMappingModel>;
        arr.push(result);
        this.form.get('port_mappings')?.reset(arr);
      }
    });
  }


  onRemovePort(keyword: any): void {
    this.portService.removeById(keyword).subscribe(result => {
      if (this.form.value.port_mappings != null) {
        this.form.value.port_mappings = this.form.value.port_mappings.filter(port => port.id !== keyword);
      }
    });
  }

  compareFn(object1: any, object2: any) {
    return object1 && object2 && object1.id === object2.id;
  }
  get f(): { [key: string]: AbstractControl } {
    return this.form.controls;
  }
}
