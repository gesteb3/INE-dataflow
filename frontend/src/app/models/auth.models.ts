export type UserRole = 'ADMIN' | 'OPERATOR' | 'ANALYST';

export interface UserInfo {
  username: string;
  full_name: string;
  role: UserRole;
}

export interface UserAdmin {
  id: string;
  username: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserCreateRequest {
  username: string;
  full_name: string;
  password: string;
  role: UserRole;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}
