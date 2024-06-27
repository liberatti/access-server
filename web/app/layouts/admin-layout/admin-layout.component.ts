import { Breakpoints, BreakpointObserver } from '@angular/cdk/layout';
import { AfterViewInit, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterModule } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import * as moment from 'moment';
import { Subject, takeUntil } from 'rxjs';
import { User } from 'web/app/models/security';
import { FrontendConfig } from 'web/app/models/shared';
import { LocalStorageService } from 'web/app/services/localstorage.service';
import { AuthService, ServerService } from 'web/app/services/security.service';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDialog } from '@angular/material/dialog';
import { AboutDialogComponent } from 'web/app/components/about-dialog/about-dialog.component';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterModule,
    MatSidenavModule, MatIconModule, MatToolbarModule,
    MatButtonModule, MatListModule, MatMenuModule,
  ],
  templateUrl: './admin-layout.component.html',
  styleUrl: './admin-layout.component.css'
})
export class AdminLayoutComponent implements OnInit, OnDestroy, AfterViewInit {
  title: string = "Access Server";
  showSpinner: boolean = false;
  user: User = <User>{};
  isAdmin: boolean = false;
  loading: boolean = false;
  config: FrontendConfig = <FrontendConfig>{ locale: { key: 'en_US' }, navGroup: "dashboard", sidenavOpened: false };

  destroyed = new Subject<void>();
  currentScreenSize: string = "";

  displayNameMap = new Map([
    [Breakpoints.XSmall, 'XSmall'],
    [Breakpoints.Small, 'Small'],
    [Breakpoints.Medium, 'Medium'],
    [Breakpoints.Large, 'Large'],
    [Breakpoints.XLarge, 'XLarge'],
  ]);

  constructor(
    private changeDetectorRef: ChangeDetectorRef,
    private authService: AuthService,
    private localStorage: LocalStorageService,
    private breakpointObserver: BreakpointObserver,
    private translate: TranslateService,
    private serverService: ServerService,
    private router: Router,
    private portDialog: MatDialog
  ) {
    breakpointObserver
      .observe([
        Breakpoints.XSmall,
        Breakpoints.Small,
        Breakpoints.Medium,
        Breakpoints.Large,
        Breakpoints.XLarge,
      ])
      .pipe(takeUntil(this.destroyed))
      .subscribe(result => {
        for (const query of Object.keys(result.breakpoints)) {
          if (result.breakpoints[query]) {
            this.currentScreenSize = this.displayNameMap.get(query) ?? 'Unknown';
          }
        }
      });

    this.config = this.localStorage.get('x-config')
  }

  isMobile() {
    return ['XSmall', 'Small'].includes(this.currentScreenSize);
  }
  ngOnDestroy() {
    this.destroyed.next();
    this.destroyed.complete();
  }
  isSidenavActive() {
    if (this.config) {
      return this.config.sidenavOpened;
    } else {
      return false;
    }
  }

  isSidenavGroup(group: string) {
    if (this.config) {
      this.config.navGroup === group
    }
    return false;
  }
  onSidenavToggle() {
    window.dispatchEvent(new Event('resize'));
    this.config = this.localStorage.get('x-config')
    this.config.sidenavOpened = !this.config.sidenavOpened;
    this.localStorage.set('x-config', this.config)
  }

  onSidenavClose() {
    this.config = this.localStorage.get('x-config')
    this.config.sidenavOpened = false;
    this.localStorage.set('x-config', this.config);
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

    this.serverService.getStatus().subscribe(data => {
      if (data.status != 'online') {
        this.router.navigate(['/wizard']);
      }
    });
  }

  showAbout() {
    const dialogRef = this.portDialog.open(AboutDialogComponent, {
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
