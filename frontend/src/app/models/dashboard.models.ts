export interface ReportSummary {
  total_batches: number;
  confirmed_batches: number;
  total_input_rows: number;
  confirmed_valid_rows: number;
  total_rejected_rows: number;
  total_validation_errors: number;
  last_confirmed_at: string | null;
}

export interface DepartmentReport {
  department_code: string;
  valid_records: number;
  urban_records: number;
  rural_records: number;
  average_age: number | null;
  average_household_size: number | null;
  average_monthly_income_gtq: number | null;
  total_monthly_income_gtq: number;
}

export interface BatchSummary {
  batch_id: string;
  file_name: string;
  status: string;
  total_rows: number;
  valid_rows: number;
  rejected_rows: number;
  warning_rows: number;
  created_at: string;
  confirmed_at: string | null;
}

export interface AuditEvent {
  action: string;
  resource_type: string;
  resource_id: string | null;
  username: string | null;
  details: Record<string, unknown>;
  created_at: string;
}
