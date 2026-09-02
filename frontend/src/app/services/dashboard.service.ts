import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuditEvent, BatchSummary, DepartmentReport, ReportSummary } from '../models/dashboard.models';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  summary(): Observable<ReportSummary> {
    return this.http.get<ReportSummary>(`${this.baseUrl}/reports/summary`);
  }

  byDepartment(): Observable<DepartmentReport[]> {
    return this.http.get<DepartmentReport[]>(`${this.baseUrl}/reports/by-department`);
  }

  batches(): Observable<BatchSummary[]> {
    return this.http.get<BatchSummary[]>(`${this.baseUrl}/batches`);
  }

  audit(): Observable<AuditEvent[]> {
    return this.http.get<AuditEvent[]>(`${this.baseUrl}/audit`);
  }
}
