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
import { AccessPolicy, PortMapping, User } from 'web/app/models/security';
import { FilterByPropertyPipe } from 'web/app/pipes/filter_by_property.pipe';
import { NotificationService } from 'web/app/services/notification.service';
import { PolicyService } from 'web/app/services/policy.service';
import { PortMappingService, UserService } from 'web/app/services/security.service';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [ReactiveFormsModule, TranslateModule, CommonModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule, MatCardModule,
    MatButtonModule, MatIcon, MatChipsModule,
    RouterModule, MatTooltipModule, MatSelectModule, MatOptionModule,
    MatIconModule, MatButtonModule, MatSlideToggleModule
  ],
  templateUrl: './user-form.component.html'
})
export class UserFormComponent implements OnInit {
  isAddMode: boolean;
  submitted = false;
  _policies: Array<AccessPolicy> = [];
  isAdmin: boolean = false;
  form = new FormGroup({
    id: new FormControl<string>(''),
    name: new FormControl<string>(''),
    username: new FormControl<string>(''),
    password: new FormControl<string>(''),
    policies: new FormControl<Array<AccessPolicy>>([]),
    role: new FormControl<String>('viewer'),
    isAdmin: new FormControl<Boolean>(false)
  });
  policyForm = new FormGroup({
    policy: new FormControl<AccessPolicy>({} as AccessPolicy)
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
      this._policies = data.data;
    });

    if (!this.isAddMode) {
      this.userService.getById(this.route.snapshot.params['id']).subscribe(data => {
        this.form.get('id')?.setValue(data.id);
        this.form.get('name')?.setValue(data.name);
        this.form.get('username')?.setValue(data.username);
        this.form.get('role')?.setValue(data.role);
        if (data.role == 'superuser') {
          this.form.get('isAdmin')?.setValue(true);
        }
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
    if (this.form.value.isAdmin) {
      formData.role = 'superuser';
    } else {
      formData.role = 'viewer';
    }
    Reflect.deleteProperty(formData, 'isAdmin');

    if (this.isAddMode) {
      Reflect.deleteProperty(formData, 'id');
      this.userService.save(formData).subscribe(() => {
        this.notificationService.openSnackBar('User saved');
        this.router.navigate(['/user']);
      });
    } else {
      this.userService.update(formData.id, formData).subscribe(() => {
        this.notificationService.openSnackBar('User updated');
        this.router.navigate(['/user']);
      });
    }
  }

  getPolicies(): Array<AccessPolicy> {
    const ids = this.form.value.policies?.map(policy => policy.id);
    return this._policies.filter(p => !ids?.includes(p.id));
  }

  onAddPolicy(): void {
    let data = this.policyForm.value.policy as AccessPolicy;
    if (this.form.value.policies != null) {
      const pExists = this.form.value.policies.some(c1 => c1.id === data.id);
      if (!pExists) {
        this.form.value.policies.push(data);
      }
    }
    this.policyForm.reset();
  }
  onRemovePolicy(keyword: any): void {
    if (this.form.value.policies != null) {
      this.form.value.policies = this.form.value.policies.filter(policy => policy.id !== keyword);
    }
  }

  compareFn(object1: any, object2: any) {
    return object1 && object2 && object1.id === object2.id;
  }
  get f(): { [key: string]: AbstractControl } {
    return this.form.controls;
  }
}
