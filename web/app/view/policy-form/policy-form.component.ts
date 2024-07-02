import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormArray, FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatOptionModule } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectChange, MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { PolicyModel, User } from 'web/app/models/security';
import { FilterByPropertyPipe } from 'web/app/pipes/filter_by_property.pipe';
import { NotificationService } from 'web/app/services/notification.service';
import { PolicyService } from 'web/app/services/policy.service';
import { UserService } from 'web/app/services/security.service';

@Component({
  selector: 'app-policy-form',
  standalone: true,
  imports: [ReactiveFormsModule, TranslateModule, CommonModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule, MatCardModule,
    MatButtonModule, MatIcon, MatChipsModule,
    RouterModule, MatTooltipModule, MatSelectModule, MatOptionModule,
    MatIconModule, MatButtonModule, FilterByPropertyPipe
  ],
  templateUrl: './policy-form.component.html',
})
export class PolicyFormComponent implements OnInit {
  isAddMode: boolean;
  submitted = false;
  __clients: Array<User> = [];

  networkForm = new FormGroup({
    addr: new FormControl<string>('')
  });

  clientForm = new FormGroup({
    client: new FormControl<User>({} as User)
  });

  form = new FormGroup({
    id: new FormControl<string>(''),
    name: new FormControl<string>(''),
    clients: new FormControl<Array<User>>([]),
    networks: new FormControl<Array<string>>([]),
    type: new FormControl<string>('')
  });

  constructor(
    private notificationService: NotificationService,
    private route: ActivatedRoute,
    private router: Router,
    private policyService: PolicyService,
    private userService: UserService

  ) {
    this.isAddMode = false;
  }

  ngOnInit(): void {
    this.isAddMode = !this.route.snapshot.params['id'];

    this.userService.get().subscribe(data => {
      this.__clients = data.data;
    });

    if (!this.isAddMode) {
      this.policyService.getById(this.route.snapshot.params['id']).subscribe(data => {
        this.form.get('id')?.setValue(data.id);
        this.form.get('name')?.setValue(data.name);
        this.form.get('networks')?.setValue(data.networks);
        this.form.get('clients')?.setValue(data.clients);

      });
    }
  }
  onSubmit() {
    this.submitted = true;
    if (this.form.status === "INVALID") {
      return;
    }
    const formData = this.form.value as PolicyModel;



    if (this.isAddMode) {
      Reflect.deleteProperty(formData, 'id');
      console.log(formData);
      this.policyService.save(formData).subscribe(() => {
        this.notificationService.openSnackBar('Policy saved');
        this.router.navigate(['/policy']);
      });
    } else {
      this.policyService.update(formData.id, formData).subscribe(() => {
        this.notificationService.openSnackBar('Policy updated');
        this.router.navigate(['/policy']);
      });
    }
  }
  onAddClient(): void {
    let data = this.clientForm.value.client as User;
    if (this.form.value.clients != null) {
      this.form.value.clients.push(data);
    }
    this.clientForm.reset();
  }
  onRemoveClient(keyword: any): void {
    if (this.form.value.clients != null) {
      this.form.value.clients = this.form.value.clients.filter(client => client.id !== keyword);
    }
  }

  onAddNetwork(): void {
    let data = this.networkForm.value.addr as string;
    if (this.form.value.networks != null) {
      this.form.value.networks.push(data);
    }
    this.networkForm.reset();
  }
  onRemoveNetwork(keyword: any): void {
    if (this.form.value.networks != null) {
      let index = this.form.value.networks.indexOf(keyword);
      if (index >= 0) {
        this.form.value.networks.splice(index, 1);
      }
    }
  }
  compareFn(object1: any, object2: any) {
    return object1 && object2 && object1.id === object2.id;
  }
  get f(): { [key: string]: AbstractControl } {
    return this.form.controls;
  }
}
