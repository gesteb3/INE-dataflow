import { JsonPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
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

type GeoPosition = [number, number];
type GeoRing = GeoPosition[];
type GeoPolygon = GeoRing[];
type GeoGeometry =
  | { type: 'Polygon'; coordinates: GeoPolygon }
  | { type: 'MultiPolygon'; coordinates: GeoPolygon[] };
type GeoFeature = { properties: { depto: string }; geometry: GeoGeometry };
type GeoFeatureCollection = { features: GeoFeature[] };

interface DepartmentMapFeature {
  name: string;
  path: string;
  value: number;
  fill: string;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule, JsonPipe],
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
  protected readonly mapError = signal<string | null>(null);
  protected readonly mapFeatures = signal<DepartmentMapFeature[]>([]);
  protected readonly mapMinValue = computed(() => {
    const values = this.mapFeatures().map((feature) => feature.value);
    return values.length ? Math.min(...values) : 0;
  });
  protected readonly mapMaxValue = computed(() => {
    const values = this.mapFeatures().map((feature) => feature.value);
    return values.length ? Math.max(...values) : 0;
  });
  protected readonly selectedBatchId = signal<string | null>(null);
  protected readonly selectedDepartmentCode = signal('');
  protected readonly visibleDepartments = computed(() => {
    const departmentCode = this.selectedDepartmentCode();
    return departmentCode
      ? this.departments().filter((item) => item.department_code === departmentCode)
      : this.departments();
  });
  protected readonly departmentSummaryRows = computed(() =>
    [...this.visibleDepartments()]
      .sort((left, right) => right.valid_records - left.valid_records)
      .slice(0, 6),
  );
  protected readonly selectedBatch = computed(() =>
    this.batches().find((item) => item.batch_id === this.selectedBatchId()) ?? null,
  );
  protected readonly departmentNames: Record<string, string> = {
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
    this.selectedBatchId.set(null);
    this.selectedDepartmentCode.set('');
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

  protected onBatchFilterChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.onBatchFilterValueChange(value);
  }

  protected onBatchFilterValueChange(value: string): void {
    this.selectedBatchId.set(value || null);
    this.selectedDepartmentCode.set('');
    this.loadReports();
  }

  protected onDepartmentFilterChange(event: Event): void {
    this.onDepartmentFilterValueChange((event.target as HTMLSelectElement).value);
  }

  protected onDepartmentFilterValueChange(value: string): void {
    this.selectedDepartmentCode.set(value);
    void this.renderDepartmentMap();
  }

  protected resetToLatestBatch(): void {
    const latest = this.batches().find((item) => item.status === 'CONFIRMED') ?? null;
    this.selectedBatchId.set(latest?.batch_id ?? null);
    this.selectedDepartmentCode.set('');
    this.loadReports();
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
    this.dashboardService.batches().subscribe({
      next: (result) => {
        this.batches.set(result);
        const latestConfirmed = result.find((item) => item.status === 'CONFIRMED');
        const selectedStillExists = result.some((item) => item.batch_id === this.selectedBatchId() && item.status === 'CONFIRMED');
        if (!selectedStillExists) this.selectedBatchId.set(latestConfirmed?.batch_id ?? null);
        this.loadReports();
      },
      error: () => {
        this.batches.set([]);
        this.loadReports();
      },
    });
    if (this.currentUser()?.role === 'ADMIN') {
      this.dashboardService.audit().subscribe({
        next: (result) => this.auditEvents.set(result),
        error: () => this.auditEvents.set([]),
      });
    }
  }

  private loadReports(): void {
    const batchId = this.selectedBatchId();
    this.dashboardService.summary(batchId).subscribe({
      next: (result) => this.summary.set(result),
      error: () => this.summary.set(null),
      complete: () => this.isLoadingDashboard.set(false),
    });
    this.dashboardService.byDepartment(batchId).subscribe({
      next: (result) => {
        this.departments.set(result);
        void this.renderDepartmentMap();
      },
      error: () => this.departments.set([]),
    });
  }

  private async renderDepartmentMap(): Promise<void> {
    if (!this.departments().length) return;
    try {
      this.mapError.set(null);
      const geoJsonResponse = await fetch('/guatemala-departments.geojson');
      if (!geoJsonResponse.ok) throw new Error('GeoJSON no disponible');
      const geoJson = await geoJsonResponse.json() as GeoFeatureCollection;
      const rows = new Map(this.departments().map((item) => [item.department_code, item.valid_records]));
      const visibleCodes = new Set(this.visibleDepartments().map((item) => item.department_code));
      const bounds = this.geoBounds(geoJson.features);
      const values = geoJson.features
        .map((feature) => this.departmentCode(feature.properties.depto))
        .filter((code): code is string => Boolean(code && visibleCodes.has(code)))
        .map((code) => rows.get(code) ?? 0);
      const minValue = values.length ? Math.min(...values) : 0;
      const maxValue = values.length ? Math.max(...values) : 0;
      const features = geoJson.features
        .map((feature) => {
          const code = this.departmentCode(feature.properties.depto);
          if (!code || !visibleCodes.has(code)) return null;
          const value = rows.get(code) ?? 0;
          return {
            name: feature.properties.depto,
            path: this.geometryPath(feature.geometry, bounds),
            value,
            fill: this.mapColor(value, minValue, maxValue),
          } satisfies DepartmentMapFeature;
        })
        .filter((feature): feature is DepartmentMapFeature => feature !== null);
      this.mapFeatures.set(features);
    } catch {
      this.mapFeatures.set([]);
      this.mapError.set('No fue posible cargar el mapa departamental.');
    }
  }

  private departmentCode(name: string): string | null {
    return Object.entries(this.departmentNames).find(([, departmentName]) => departmentName === name)?.[0] ?? null;
  }

  private geoBounds(features: GeoFeature[]): { minLon: number; maxLon: number; minLat: number; maxLat: number } {
    const positions = features.flatMap((feature) => this.geometryPositions(feature.geometry));
    const longitudes = positions.map(([longitude]) => longitude);
    const latitudes = positions.map(([, latitude]) => latitude);
    return {
      minLon: Math.min(...longitudes),
      maxLon: Math.max(...longitudes),
      minLat: Math.min(...latitudes),
      maxLat: Math.max(...latitudes),
    };
  }

  private geometryPositions(geometry: GeoGeometry): GeoPosition[] {
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    return polygons.flatMap((polygon) => polygon.flatMap((ring) => ring));
  }

  private geometryPath(
    geometry: GeoGeometry,
    bounds: { minLon: number; maxLon: number; minLat: number; maxLat: number },
  ): string {
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    const width = bounds.maxLon - bounds.minLon;
    const height = bounds.maxLat - bounds.minLat;
    return polygons.map((polygon) => polygon.map((ring) => {
      const points = ring.map(([longitude, latitude]) => {
        const x = 35 + ((longitude - bounds.minLon) / width) * 930;
        const y = 25 + ((bounds.maxLat - latitude) / height) * 850;
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      });
      return `M${points.join(' L')} Z`;
    }).join(' ')).join(' ');
  }

  private mapColor(value: number, minValue: number, maxValue: number): string {
    const ratio = maxValue === minValue ? 0.55 : (value - minValue) / (maxValue - minValue);
    const start = [219, 237, 251];
    const end = [12, 45, 89];
    const channel = (index: number) => Math.round(start[index] + (end[index] - start[index]) * ratio);
    return `rgb(${channel(0)}, ${channel(1)}, ${channel(2)})`;
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
