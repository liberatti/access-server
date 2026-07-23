import { AfterViewInit, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterModule } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import moment from 'moment';
import { User } from 'web/app/models/security';
import { FrontendConfig } from 'web/app/models/shared';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { AuthService, ServerService } from 'web/app/services/security.service';
import { MatDialog } from '@angular/material/dialog';
import { AboutDialogComponent } from 'web/app/components/about-dialog/about-dialog.component';
import { environment } from 'web/environments/environment';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [
    RouterModule,
    MatIconModule,
    MatToolbarModule,
    MatButtonModule,
    MatMenuModule,
  ],
  templateUrl: './admin-layout.component.html',
  styleUrl: './admin-layout.component.css'
})
export class AdminLayoutComponent implements OnInit, AfterViewInit {
  title: string = "Access Server";
  version: string = environment.version;
  user: User = <User>{};
  loading: boolean = false;
  config: FrontendConfig = <FrontendConfig>{ locale: { key: 'en_US' }, navGroup: "dashboard" };

  constructor(
    private changeDetectorRef: ChangeDetectorRef,
    private authService: AuthService,
    private localStorage: LocalStorageService,
    private translate: TranslateService,
    private serverService: ServerService,
    private router: Router,
    private dialog: MatDialog
  ) {
    this.config = this.localStorage.get('x-config');
  }

  logout() {
    this.localStorage.remove('x-auth');
    this.localStorage.remove('x-user');
    this.router.navigate(['/login']);
  }

  ngOnInit(): void {
    this.translate.setDefaultLang('en_US');
    if (!window.localStorage['x-user']) {
      this.authService.getCurrentUser().subscribe(data => {
        this.localStorage.set('x-user', data);
        this.user = data;
      });
    } else {
      this.user = this.localStorage.get('x-user');
    }
  }

  showAbout() {
    this.dialog.open(AboutDialogComponent, {
      width: '450px'
    });
  }

  ngAfterViewInit(): void {
    if (window.localStorage['x-config']) {
      this.config = this.localStorage.get('x-config');
      this.translate.use(this.config.locale.key);
      moment.locale(this.config.locale.key);
    }
    this.changeDetectorRef.detectChanges();
  }
}
