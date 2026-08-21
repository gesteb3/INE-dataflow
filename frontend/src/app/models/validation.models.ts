export type ValidationStatus =
  | 'READY_FOR_CONFIRMATION'
  | 'REVIEW_REQUIRED'
  | 'REJECTED';

export interface ValidationIssue {
  code: string;
  severity: 'ERROR' | 'WARNING';
  row: number | null;
  column: string | null;
  message: string;
  value: string | null;
}

export interface ValidationResponse {
  batch_id: string;
  file_name: string;
  status: ValidationStatus;
  total_rows: number;
  valid_rows: number;
  rejected_rows: number;
  warning_rows: number;
  issues: ValidationIssue[];
}

export interface ConfirmationResponse {
  batch_id: string;
  status: 'CONFIRMED';
  valid_rows: number;
  confirmed_at: string;
}
