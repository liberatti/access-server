import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
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
import { switchMap, interval, takeWhile, catchError, of } from 'rxjs';
import { ServerConfig } from 'web/app/models/shared';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { AuthService, ServerService } from 'web/app/services/security.service';

@Component({
  selector: 'app-wizard',
  standalone: true,
  imports: [RouterModule, FormsModule, ReactiveFormsModule, CommonModule,
    MatIconModule, MatButtonModule, MatFormFieldModule,
    MatCardModule, MatProgressBarModule, MatInputModule,
    MatTooltipModule, MatSelectModule, MatOptionModule
  ],
  templateUrl: './wizard.component.html',
  styleUrl: './wizard.component.css'
})
export class WizardComponent {

  form = new FormGroup({
    status: new FormControl<string>(''),
  });

  constructor(private router: Router,
    private auth: AuthService, private http: HttpClient,
    private localStorage: LocalStorageService,
    private serverService: ServerService) {
  }

  ngOnInit() {
    // Initial check
    this.serverService.getStatus().pipe(
      catchError(() => of({ status: 'offline' } as ServerConfig))
    ).subscribe(data => {
      this.form.get("status")?.setValue(data.status);
      if (data.status === 'online') {
        this.router.navigate(['/login']);
      }
    });

    // Polling check every 3 seconds
    interval(3000).pipe(
      switchMap(() => this.serverService.getStatus().pipe(
        catchError(() => of({ status: 'offline' } as ServerConfig))
      )),
      takeWhile((data) => data.status !== 'online', true)
    ).subscribe(data => {
      this.form.get("status")?.setValue(data.status);
      if (data.status === 'online') {
        this.router.navigate(['/login']);
      }
    });
  }
}