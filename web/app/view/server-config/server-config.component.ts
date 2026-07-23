import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ServerService } from 'web/app/services/security.service';

@Component({
  selector: 'app-server-config',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSnackBarModule,
    TranslateModule
  ],
  templateUrl: './server-config.component.html',
  styleUrl: './server-config.component.css'
})
export class ServerConfigComponent implements OnInit {
  form = new FormGroup({
    name: new FormControl<string>('AccessServer', { validators: [Validators.required] }),
    network: new FormControl<string>('10.8.0.0', { validators: [Validators.required] }),
    netmask: new FormControl<string>('255.255.255.0', { validators: [Validators.required] })
  });

  networkForm = new FormGroup({
    addr: new FormControl<string>('')
  });

  networks: string[] = [];

  constructor(
    private serverService: ServerService,
    private snackBar: MatSnackBar,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.serverService.getConfig().subscribe({
      next: (res: any) => {
        const data = res?.data || res || {};
        if (data) {
          this.form.patchValue({
            name: data.name || 'AccessServer',
            network: data.network || '10.8.0.0',
            netmask: data.netmask || '255.255.255.0'
          });
        }
      },
      error: () => {
        // Fallback default load
      }
    });
  }

  onAddNetwork(): void {
    const val = this.networkForm.value.addr?.trim();
    if (val && !this.networks.includes(val)) {
      this.networks.push(val);
      this.networkForm.reset();
    }
  }

  onRemoveNetwork(net: string): void {
    this.networks = this.networks.filter(n => n !== net);
  }

  onSubmit(): void {
    if (this.form.invalid) {
      return;
    }

    const payload = {
      ...this.form.value,
      networks: this.networks
    };

    this.serverService.updateConfig(payload).subscribe({
      next: () => {
        this.snackBar.open('Server configuration updated & restarted successfully!', 'Close', { duration: 3000 });
      },
      error: (err) => {
        this.snackBar.open('Failed to update server configuration: ' + (err.message || 'Error'), 'Close', { duration: 4000 });
      }
    });
  }
}
