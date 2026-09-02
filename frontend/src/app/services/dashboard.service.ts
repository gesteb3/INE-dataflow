import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuditEvent, BatchSummary, DepartmentReport, ReportSummary } from '../models/dashboard.models';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  summary(batchId: string | null = null): Observable<ReportSummary> {
    return this.http.get<ReportSummary>(`${this.baseUrl}/reports/summary`, { params: this.batchParams(batchId) });
  }

  byDepartment(batchId: string | null = null): Observable<DepartmentReport[]> {
    return this.http.get<DepartmentReport[]>(`${this.baseUrl}/reports/by-department`, { params: this.batchParams(batchId) });
  }

  batches(): Observable<BatchSummary[]> {
    return this.http.get<BatchSummary[]>(`${this.baseUrl}/batches`);
  }

  audit(): Observable<AuditEvent[]> {
    return this.http.get<AuditEvent[]>(`${this.baseUrl}/audit`);
  }

  exportIssues(batchId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/batches/${batchId}/issues.csv`, { responseType: 'blob' });
  }

  private batchParams(batchId: string | null): HttpParams {
    return batchId ? new HttpParams().set('batch_id', batchId) : new HttpParams();
  }
}
