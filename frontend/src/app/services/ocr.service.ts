import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { OcrFileResult } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class OcrService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  preview(files: File[]): Observable<OcrFileResult[]> {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file, file.name));
    return this.http.post<OcrFileResult[]>(`${this.baseUrl}/ocr/preview`, formData);
  }
}
