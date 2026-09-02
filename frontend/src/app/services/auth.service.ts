import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import { LoginRequest, TokenResponse, UserInfo } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenKey = 'ine_dataflow_access_token';
  private readonly userKey = 'ine_dataflow_user';
  readonly currentUser = signal<UserInfo | null>(this.readUser());

  login(credentials: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, credentials).pipe(
      tap((response) => {
        localStorage.setItem(this.tokenKey, response.access_token);
        localStorage.setItem(this.userKey, JSON.stringify(response.user));
        this.currentUser.set(response.user);
      }),
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    this.currentUser.set(null);
  }

  token(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  private readUser(): UserInfo | null {
    try {
      const saved = localStorage.getItem(this.userKey);
      return saved ? (JSON.parse(saved) as UserInfo) : null;
    } catch {
      return null;
    }
  }
}
