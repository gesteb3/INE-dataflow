import { JsonPipe } from '@angular/common';
import { AfterViewInit, Component, computed, ElementRef, inject, OnInit, signal, ViewChild } from '@angular/core';

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
export class App implements OnInit, AfterViewInit {
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
  protected readonly mapError = signal<string | null>(null);
  @ViewChild('departmentMap') private departmentMap?: ElementRef<HTMLDivElement>;
  private mapReady = false;
  private readonly departmentNames: Record<string, string> = {
    '01': 'Guatemala', '02': 'El Progreso', '03': 'Sacatepéquez', '04': 'Chimaltenango',
    '05': 'Escuintla', '06': 'Santa Rosa', '07': 'Sololá', '08': 'Totonicapán',
    '09': 'Quetzaltenango', '10': 'Suchitepéquez', '11': 'Retalhuleu', '12': 'San Marcos',
    '13': 'Huehuetenango', '14': 'Quiché', '15': 'Baja Verapaz', '16': 'Alta Verapaz',
    '17': 'Petén', '18': 'Izabal', '19': 'Zacapa', '20': 'Chiquimula', '21': 'Jalapa',
    '22': 'Jutiapa',
  };

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

  ngAfterViewInit(): void {
    this.mapReady = true;
    void this.renderDepartmentMap();
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

  protected startCorrection(): void {
    this.activeSection.set('upload');
    this.selectedFile.set(null);
    this.validation.set(null);
    this.confirmation.set(null);
    this.errorMessage.set(null);
  }

  protected exportIssues(batchId: string): void {
    this.dashboardService.exportIssues(batchId).subscribe({
      next: (file) => {
        const url = URL.createObjectURL(file);
        const link = document.createElement('a');
        link.href = url;
        link.download = `errores-${batchId}.csv`;
        link.click();
        URL.revokeObjectURL(url);
      },
      error: () => this.errorMessage.set('No fue posible exportar las incidencias del lote.'),
    });
  }

  protected loadDashboard(): void {
    this.isLoadingDashboard.set(true);
    this.dashboardService.summary().subscribe({
      next: (result) => this.summary.set(result),
      error: () => this.summary.set(null),
    });
    this.dashboardService.byDepartment().subscribe({
      next: (result) => {
        this.departments.set(result);
        void this.renderDepartmentMap();
      },
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

  private async renderDepartmentMap(): Promise<void> {
    if (!this.mapReady || !this.departmentMap || !this.departments().length) return;
    try {
      this.mapError.set(null);
      const geoJsonResponse = await fetch('/guatemala-departments.geojson');
      if (!geoJsonResponse.ok) throw new Error('GeoJSON no disponible');
      const geoJson = await geoJsonResponse.json();
      const plotlyModule = await import('plotly.js-dist-min');
      const plotly = plotlyModule.default;
      const rows = this.departments().map((item) => ({
        department: this.departmentNames[item.department_code] ?? item.department_code,
        value: item.valid_records,
      }));
      await plotly.newPlot(this.departmentMap.nativeElement, [{
        type: 'choropleth',
        geojson: geoJson,
        featureidkey: 'properties.depto',
        locations: rows.map((row) => row.department),
        z: rows.map((row) => row.value),
        colorscale: [[0, '#e6f2fc'], [0.5, '#5a9ed0'], [1, '#0c2d59']],
        marker: { line: { color: '#ffffff', width: 1 } },
        hovertemplate: '<b>%{location}</b><br>Registros válidos: %{z}<extra></extra>',
      }], {
        geo: { fitbounds: 'locations', visible: false, bgcolor: 'rgba(0,0,0,0)' },
        margin: { t: 0, r: 0, b: 0, l: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
      }, { responsive: true, displayModeBar: false });
    } catch {
      this.mapError.set('No fue posible cargar el mapa departamental.');
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
