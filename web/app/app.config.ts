import { ApplicationConfig, importProvidersFrom, InjectionToken } from '@angular/core';
import { provideRouter, withHashLocation } from '@angular/router';
import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { HttpClient, provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { JwtInterceptor } from './interceptors/jwt.interceptor';

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}
export const REST_API_URL = new InjectionToken<string>('REST_API_URL');

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: REST_API_URL, useValue: "http://localhost:5000/api" },
    //{ provide: 'REST_API_URL', useValue: "" },
    provideRouter(routes, withHashLocation()),
    provideAnimationsAsync(),
    provideHttpClient(
      withFetch(), withInterceptors([JwtInterceptor])
    ),
    importProvidersFrom(TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }
    }))]
};
