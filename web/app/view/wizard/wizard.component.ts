import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatOptionModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule } from '@angular/router';
import { map, switchMap, interval, takeWhile, filter, catchError, of } from 'rxjs';
import { User } from 'web/app/models/security';
import { Language, FrontendConfig, ServerConfig } from 'web/app/models/shared';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { AuthService, ServerService } from 'web/app/services/security.service';

@Component({
  selector: 'app-wizard',
  standalone: true,
  imports: [RouterModule, FormsModule, ReactiveFormsModule,CommonModule,
    MatIconModule, MatButtonModule, MatFormFieldModule,
    MatCardModule, MatProgressBarModule, MatInputModule,
    MatTooltipModule, MatSelectModule, MatOptionModule
  ],

  templateUrl: './wizard.component.html',
  styleUrl: './wizard.component.css'
})
export class WizardComponent {

  form = new FormGroup({
    name: new FormControl<string>('default'),
    subnet: new FormControl<string>('10.8.0.0 255.255.255.0'),
    public_address: new FormControl<string>('172.16.93.1'),
    public_port: new FormControl<number>(1194),
    admin_user: new FormControl<string>('admin'),
    admin_pass: new FormControl<string>('admin'),
    status: new FormControl<string>(''),
  });

  constructor(private router: Router,
    private auth: AuthService, private http: HttpClient,
    private localStorage: LocalStorageService,
    private serverService: ServerService) {
  }

  ngOnInit() {
    this.serverService.getStatus().subscribe(data => {
      this.form.get("status")?.setValue(data.status)
      if (data.status == 'online') {
        this.router.navigate(['/login']);
      }
    });
  }
  onSubmit() {
    let formData = this.form.value as ServerConfig;


    this.serverService.activate(formData).pipe(
      map(data => {
        formData.status = data.status;
        return data;
      }),
      switchMap(() => interval(5000).pipe(
        switchMap(() => this.serverService.getStatus(),),
        takeWhile((r) => r.status !== 'online', true))
      )
    ).subscribe(data => {
      if (data) {
        this.form.get("status")?.setValue(data.status)
        if (data.status == 'online') {
          this.router.navigate(['/login']);
        }
      }
    });
  }
}