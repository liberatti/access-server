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
import { User } from 'web/app/models/security';
import { Language, FrontendConfig } from 'web/app/models/shared';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { AuthService } from 'web/app/services/security.service';

@Component({
  selector: 'app-sigin',
  standalone: true,
  imports: [RouterModule, FormsModule, ReactiveFormsModule,
    MatIconModule, MatButtonModule, MatFormFieldModule,
    MatCardModule, MatProgressBarModule, MatInputModule,
    MatTooltipModule, MatSelectModule, MatOptionModule
  ],

  templateUrl: './sigin.component.html',
  styleUrl: './sigin.component.css'
})
export class SiginComponent {
  locales = [] as Array<Language>;

  form = new FormGroup({
    username: new FormControl<string>('', {
      validators: [
        Validators.required,
      ],
    }),
    password: new FormControl<string>('', {
      validators: [
        Validators.required,
      ],
    }),
    locale: new FormControl<string>('pt_BR'),
  });

  constructor(private router: Router,
    private auth: AuthService, private http: HttpClient,
    private localStorage: LocalStorageService) {
  }

  ngOnInit() {
    this.logout();
    this.locales = [
      { id: 'en_US', name: "English (US)" },
      { id: 'pt_BR', name: "Português (BR)" },
    ];
  }

  login() {
    if (this.form.status === "INVALID") {
      return;
    }

    const formData = this.form.value as User;
    this.auth.login(formData).subscribe(data => {
      this.localStorage.set('x-auth', data);
      this.http.get('./assets/i18n/' + formData.locale + '.json').subscribe((data: any) => {
        let lc = {
          key: formData.locale,
          display: data.format.display,
          parse: data.format.parse
        }
        this.localStorage.set('x-config', <FrontendConfig>{ locale: lc, navGroup: "dashboard", navResource: "system" });
        this.router.navigate(['/user']);
      });
    });
  }

  logout() {
    this.auth.logout();
    this.localStorage.remove('x-auth');
    this.localStorage.remove('x-user');
  }

  resetPassword() {
    this.router.navigate(['/auth/password-reset-request']);
  }
}
