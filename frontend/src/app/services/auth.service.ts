import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/login/`, { username, password }).pipe(
      tap(response => {
        localStorage.setItem('access', response.access);
        localStorage.setItem('refresh', response.refresh);
        localStorage.setItem('username', response.username);
      })
    );
  }

  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register/`, { username, password });
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/logout/`, { refresh: localStorage.getItem('refresh') });
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access');
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access');
  }

  clearTokens(): void {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
  }
}
