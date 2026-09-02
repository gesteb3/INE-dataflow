import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { UserAdmin, UserCreateRequest, UserRole } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  list(): Observable<UserAdmin[]> {
    return this.http.get<UserAdmin[]>(`${this.baseUrl}/users`);
  }

  create(payload: UserCreateRequest): Observable<UserAdmin> {
    return this.http.post<UserAdmin>(`${this.baseUrl}/users`, payload);
  }

  update(userId: string, payload: { full_name?: string; role?: UserRole; is_active?: boolean }): Observable<UserAdmin> {
    return this.http.patch<UserAdmin>(`${this.baseUrl}/users/${userId}`, payload);
  }
}
