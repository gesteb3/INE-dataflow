import { JsonPipe, KeyValuePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component, computed, inject, OnInit, signal } from '@angular/core';

import {
  ConfirmationResponse,
  ValidationResponse,
  ValidationStatus,
} from './models/validation.models';
import { AuditEvent, BatchSummary, DepartmentReport, ReportSummary } from './models/dashboard.models';
import { OcrFileResult, UserAdmin, UserRole } from './models/auth.models';
import { AuthService } from './services/auth.service';
import { DashboardService } from './services/dashboard.service';
import { UploadService } from './services/upload.service';
import { UserService } from './services/user.service';
import { OcrService } from './services/ocr.service';

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

interface DashboardAlert {
  severity: 'WARNING' | 'CRITICAL';
  title: string;
  detail: string;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule, JsonPipe, KeyValuePipe],
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly dashboardService = inject(DashboardService);
  private readonly uploadService = inject(UploadService);
  private readonly userService = inject(UserService);
  private readonly ocrService = inject(OcrService);

  protected readonly currentUser = this.authService.currentUser;
  protected readonly activeSection = signal<'dashboard' | 'upload' | 'ocr' | 'batches' | 'audit' | 'users'>('dashboard');
  protected readonly isLoadingDashboard = signal(false);
  protected readonly databaseOnline = signal(true);
  protected readonly summary = signal<ReportSummary | null>(null);
  protected readonly departments = signal<DepartmentReport[]>([]);
  protected readonly batches = signal<BatchSummary[]>([]);
  protected readonly auditEvents = signal<AuditEvent[]>([]);
  protected readonly users = signal<UserAdmin[]>([]);
  protected readonly isSavingUser = signal(false);
  protected readonly userMessage = signal<string | null>(null);
  protected readonly userError = signal<string | null>(null);
  protected readonly newUserUsername = signal('');
  protected readonly newUserFullName = signal('');
  protected readonly newUserPassword = signal('');
  protected readonly newUserRole = signal<UserRole>('OPERATOR');
  protected readonly selectedOcrFiles = signal<File[]>([]);
  protected readonly ocrResults = signal<OcrFileResult[]>([]);
  protected readonly selectedOcrFileNames = computed(() => this.selectedOcrFiles().map((file) => file.name).join(', '));
  protected readonly isProcessingOcr = signal(false);
  protected readonly ocrError = signal<string | null>(null);
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
  protected readonly dashboardAlerts = computed<DashboardAlert[]>(() => {
    const alerts: DashboardAlert[] = [];
    if (!this.databaseOnline()) alerts.push({ severity: 'CRITICAL', title: 'Base de datos no disponible', detail: 'Revisa el contenedor PostgreSQL antes de procesar nuevos lotes.' });
    const report = this.summary();
    if (report && report.total_rejected_rows > 0) alerts.push({ severity: 'WARNING', title: 'Hay registros rechazados', detail: `${this.formatNumber(report.total_rejected_rows)} filas requieren corrección.` });
    if (report && report.total_validation_errors > 0) alerts.push({ severity: 'WARNING', title: 'Incidencias de calidad detectadas', detail: `${this.formatNumber(report.total_validation_errors)} incidencias están disponibles para auditoría.` });
    return alerts;
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
    this.users.set([]);
    this.selectedBatchId.set(null);
    this.selectedDepartmentCode.set('');
  }

  protected navigate(section: 'dashboard' | 'upload' | 'ocr' | 'batches' | 'audit' | 'users'): void {
    this.activeSection.set(section);
    if (section === 'dashboard' || section === 'batches' || section === 'audit') {
      this.loadDashboard();
    }
    if (section === 'users' && this.currentUser()?.role === 'ADMIN') this.loadUsers();
  }

  protected onOcrFilesSelected(event: Event): void {
    const files = Array.from((event.target as HTMLInputElement).files ?? []);
    const totalBytes = files.reduce((total, file) => total + file.size, 0);
    if (!files.length) return;
    if (files.length > 5) {
      this.ocrError.set('Puedes seleccionar como máximo 5 archivos.');
      this.selectedOcrFiles.set([]);
      return;
    }
    if (files.some((file) => file.size > 10 * 1024 * 1024)) {
      this.ocrError.set('Cada archivo OCR debe pesar como máximo 10 MB.');
      this.selectedOcrFiles.set([]);
      return;
    }
    if (totalBytes > 25 * 1024 * 1024) {
      this.ocrError.set('La selección completa debe pesar como máximo 25 MB.');
      this.selectedOcrFiles.set([]);
      return;
    }
    this.ocrError.set(null);
    this.ocrResults.set([]);
    this.selectedOcrFiles.set(files);
  }

  protected processOcr(): void {
    const files = this.selectedOcrFiles();
    if (!files.length) return;
    this.isProcessingOcr.set(true);
    this.ocrError.set(null);
    this.ocrService.preview(files).subscribe({
      next: (results) => {
        this.ocrResults.set(results);
        this.isProcessingOcr.set(false);
      },
      error: (error) => {
        this.ocrError.set(error.error?.detail ?? 'No fue posible procesar los archivos OCR.');
        this.isProcessingOcr.set(false);
      },
    });
  }

  protected loadUsers(): void {
    this.userError.set(null);
    this.userService.list().subscribe({
      next: (users) => this.users.set(users),
      error: (error) => this.userError.set(error.status === 403 ? 'No tienes permisos para consultar usuarios.' : 'No fue posible cargar los usuarios.'),
    });
  }

  protected createUser(): void {
    if (!this.newUserUsername() || !this.newUserFullName() || this.newUserPassword().length < 8) {
      this.userError.set('Completa usuario, nombre y una contraseña de mínimo 8 caracteres.');
      return;
    }
    this.isSavingUser.set(true);
    this.userError.set(null);
    this.userMessage.set(null);
    this.userService.create({ username: this.newUserUsername(), full_name: this.newUserFullName(), password: this.newUserPassword(), role: this.newUserRole() }).subscribe({
      next: () => {
        this.newUserUsername.set('');
        this.newUserFullName.set('');
        this.newUserPassword.set('');
        this.newUserRole.set('OPERATOR');
        this.userMessage.set('Usuario creado y registrado en auditoría.');
        this.isSavingUser.set(false);
        this.loadUsers();
        this.loadDashboard();
      },
      error: (error) => {
        this.userError.set(error.status === 409 ? 'Ese usuario ya existe.' : 'No fue posible crear el usuario.');
        this.isSavingUser.set(false);
      },
    });
  }

  protected changeUserRole(user: UserAdmin, event: Event): void {
    const role = (event.target as HTMLSelectElement).value as UserRole;
    this.updateUser(user, { role });
  }

  protected toggleUser(user: UserAdmin): void {
    this.updateUser(user, { is_active: !user.is_active });
  }

  private updateUser(user: UserAdmin, payload: { role?: UserRole; is_active?: boolean }): void {
    this.isSavingUser.set(true);
    this.userError.set(null);
    this.userMessage.set(null);
    this.userService.update(user.id, payload).subscribe({
      next: () => {
        this.userMessage.set('Cambios guardados y registrados en auditoría.');
        this.isSavingUser.set(false);
        this.loadUsers();
        this.loadDashboard();
      },
      error: (error) => {
        this.userError.set(error.status === 400 ? (error.error?.detail ?? 'No se puede realizar ese cambio.') : 'No fue posible actualizar el usuario.');
        this.isSavingUser.set(false);
        this.loadUsers();
      },
    });
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

  protected exportValidRecords(batchId: string): void {
    this.dashboardService.exportValidRecords(batchId).subscribe({
      next: (file) => {
        const url = URL.createObjectURL(file);
        const link = document.createElement('a');
        link.href = url;
        link.download = `encuesta-limpia-${batchId}.csv`;
        link.click();
        URL.revokeObjectURL(url);
      },
      error: () => this.errorMessage.set('No fue posible exportar la encuesta limpia.'),
    });
  }

  protected loadDashboard(): void {
    this.isLoadingDashboard.set(true);
    this.dashboardService.databaseHealth().subscribe({
      next: () => this.databaseOnline.set(true),
      error: () => this.databaseOnline.set(false),
    });
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
    return { ADMIN: 'Administrador', OPERATOR: 'Operador' }[role];
  }
}
