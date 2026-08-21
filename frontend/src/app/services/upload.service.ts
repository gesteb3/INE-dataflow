import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  ConfirmationResponse,
  ValidationResponse,
} from '../models/validation.models';

@Injectable({ providedIn: 'root' })
export class UploadService {
  private readonly http = inject(HttpClient);
  private readonly uploadsUrl = `${environment.apiUrl}/uploads`;

  validate(file: File): Observable<ValidationResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ValidationResponse>(
      `${this.uploadsUrl}/validate`,
      formData,
    );
  }

  confirm(batchId: string): Observable<ConfirmationResponse> {
    return this.http.post<ConfirmationResponse>(
      `${this.uploadsUrl}/${batchId}/confirm`,
      {},
    );
  }
}
