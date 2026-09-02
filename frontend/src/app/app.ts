import { JsonPipe } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';

import {
  ConfirmationResponse,
  ValidationResponse,
  ValidationStatus,
} from './models/validation.models';
import { AuditEvent, BatchSummary, DepartmentReport, ReportSummary } from './models/dashboard.models';
import { UserRole } from './models/auth.models';
import { AuthService } from './services/auth.service';
import { DashboardService } from './services/dashboard.service';
import { UploadService } from './services/upload.service';

@Component({
  selector: 'app-root',
  imports: [JsonPipe],
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly dashboardService = inject(DashboardService);
  private readonly uploadService = inject(UploadService);

  protected readonly currentUser = this.authService.currentUser;
  protected readonly activeSection = signal<'dashboard' | 'upload' | 'batches' | 'audit'>('dashboard');
  protected readonly isLoadingDashboard = signal(false);
  protected readonly summary = signal<ReportSummary | null>(null);
  protected readonly departments = signal<DepartmentReport[]>([]);
  protected readonly batches = signal<BatchSummary[]>([]);
  protected readonly auditEvents = signal<AuditEvent[]>([]);

  protected readonly loginUsername = signal('admin@ine.local');
  protected readonly loginPassword = signal('INEDataFlow2026!');
  protected readonly isLoggingIn = signal(false);
  protected readonly loginError = signal<string | null>(null);
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly validation = signal<ValidationResponse | null>(null);
  protected readonly confirmation = signal<ConfirmationResponse | null>(null);
  protected readonly isProcessing = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly canConfirm = computed(() => {
    const result = this.validation();
    return Boolean(result && result.valid_rows > 0 && !this.confirmation());
  });

  ngOnInit(): void {
    if (this.currentUser()) {
      this.loadDashboard();
    }
  }

  protected submitLogin(): void {
    this.isLoggingIn.set(true);
    this.loginError.set(null);
    this.authService.login({ username: this.loginUsername(), password: this.loginPassword() }).subscribe({
      next: () => {
        this.isLoggingIn.set(false);
        this.activeSection.set('dashboard');
        this.loadDashboard();
      },
      error: (error) => {
        this.loginError.set(error.status === 401 ? 'Usuario o contraseña incorrectos.' : 'No fue posible conectar con la API.');
        this.isLoggingIn.set(false);
      },
    });
  }

  protected logout(): void {
    this.authService.logout();
    this.summary.set(null);
    this.departments.set([]);
    this.batches.set([]);
    this.auditEvents.set([]);
  }

  protected navigate(section: 'dashboard' | 'upload' | 'batches' | 'audit'): void {
    this.activeSection.set(section);
    if (section === 'dashboard' || section === 'batches' || section === 'audit') {
      this.loadDashboard();
    }
  }

  protected loadDashboard(): void {
    this.isLoadingDashboard.set(true);
    this.dashboardService.summary().subscribe({
      next: (result) => this.summary.set(result),
      error: () => this.summary.set(null),
    });
    this.dashboardService.byDepartment().subscribe({
      next: (result) => this.departments.set(result),
      error: () => this.departments.set([]),
    });
    this.dashboardService.batches().subscribe({
      next: (result) => this.batches.set(result),
      error: () => this.batches.set([]),
      complete: () => this.isLoadingDashboard.set(false),
    });
    if (this.currentUser()?.role === 'ADMIN') {
      this.dashboardService.audit().subscribe({
        next: (result) => this.auditEvents.set(result),
        error: () => this.auditEvents.set([]),
      });
    }
  }

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
    this.validation.set(null);
    this.confirmation.set(null);
    this.errorMessage.set(null);
  }

  protected validateFile(): void {
    const file = this.selectedFile();
    if (!file) {
      return;
    }

    this.isProcessing.set(true);
    this.validation.set(null);
    this.confirmation.set(null);
    this.errorMessage.set(null);

    this.uploadService.validate(file).subscribe({
      next: (result) => {
        this.validation.set(result);
        this.isProcessing.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'No fue posible validar el archivo. Verifica que la API esté disponible.',
        );
        this.isProcessing.set(false);
      },
    });
  }

  protected confirmBatch(): void {
    const result = this.validation();
    if (!result || !this.canConfirm()) {
      return;
    }

    this.isProcessing.set(true);
    this.errorMessage.set(null);
    this.uploadService.confirm(result.batch_id).subscribe({
      next: (confirmation) => {
        this.confirmation.set(confirmation);
        this.isProcessing.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'No fue posible confirmar el lote. Puede que ya haya sido confirmado.',
        );
        this.isProcessing.set(false);
      },
    });
  }

  protected formatFileSize(bytes: number): string {
    if (bytes < 1024) {
      return `${bytes} B`;
    }
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  protected statusLabel(status: ValidationStatus): string {
    const labels: Record<ValidationStatus, string> = {
      READY_FOR_CONFIRMATION: 'Listo para confirmar',
      REVIEW_REQUIRED: 'Revisión requerida',
      REJECTED: 'Lote rechazado',
    };
    return labels[status];
  }

  protected formatNumber(value: number | null | undefined): string {
    return new Intl.NumberFormat('es-GT').format(value ?? 0);
  }

  protected formatCurrency(value: number | null | undefined): string {
    return new Intl.NumberFormat('es-GT', { style: 'currency', currency: 'GTQ', maximumFractionDigits: 0 }).format(value ?? 0);
  }

  protected formatDate(value: string | null | undefined): string {
    if (!value) return '—';
    return new Intl.DateTimeFormat('es-GT', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
  }

  protected departmentWidth(value: number): number {
    const max = Math.max(...this.departments().map((item) => item.valid_records), 1);
    return Math.max(5, Math.round((value / max) * 100));
  }

  protected roleLabel(role: UserRole): string {
    return { ADMIN: 'Administrador', OPERATOR: 'Operador', ANALYST: 'Analista' }[role];
  }
}
