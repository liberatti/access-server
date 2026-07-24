import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { TranslateModule } from '@ngx-translate/core';

export interface SessionData {
  remote_ip: string;
  local_ip: string;
  remote_port?: number;
  state?: string;
  created_at?: string;
  bytes_received?: number;
  bytes_sent?: number;
}

export interface SessionsDialogData {
  username: string;
  sessions: SessionData[];
}

@Component({
  selector: 'app-sessions-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    TranslateModule
  ],
  templateUrl: './sessions-dialog.component.html',
  styles: [`
    .sessions-dialog-content {
      min-width: 320px;
      max-width: 500px;
    }
    .session-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 8px 0;
    }
    .session-card {
      background: var(--background-darker, rgba(0, 0, 0, 0.04));
      border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
      border-radius: 8px;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .session-header {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-primary);
    }
    .session-icon {
      color: var(--primary-color, #7b2cbf);
    }
    .session-title {
      font-size: 14px;
    }
    .session-details {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding-left: 32px;
      font-size: 13px;
      color: var(--text-secondary, #666);
    }
    .detail-item {
      line-height: 1.4;
      word-break: break-all;
    }
    .stats-container {
      display: flex;
      gap: 12px;
      margin-top: 4px;
      flex-wrap: wrap;
    }
    .stat-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: bold;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .stat-badge mat-icon {
      font-size: 14px;
      width: 14px;
      height: 14px;
    }
    .stat-badge.down {
      background: rgba(46, 196, 182, 0.15);
      color: #2ec4b6;
    }
    .stat-badge.up {
      background: rgba(231, 111, 81, 0.15);
      color: #e76f51;
    }
  `]
})
export class SessionsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<SessionsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SessionsDialogData
  ) {}

  formatBytes(bytes: number | undefined): string {
    if (bytes === undefined || bytes === null) return '0 B';
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
