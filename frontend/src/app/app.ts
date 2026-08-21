import { Component, computed, inject, signal } from '@angular/core';

import {
  ConfirmationResponse,
  ValidationResponse,
  ValidationStatus,
} from './models/validation.models';
import { UploadService } from './services/upload.service';

@Component({
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
})
export class App {
  private readonly uploadService = inject(UploadService);

  protected readonly selectedFile = signal<File | null>(null);
  protected readonly validation = signal<ValidationResponse | null>(null);
  protected readonly confirmation = signal<ConfirmationResponse | null>(null);
  protected readonly isProcessing = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly canConfirm = computed(() => {
    const result = this.validation();
    return Boolean(result && result.valid_rows > 0 && !this.confirmation());
  });

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
}
