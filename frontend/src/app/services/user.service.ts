import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserProfile } from '../models/user-profile';

@Injectable({ providedIn: 'root' })
export class UserService {
  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getProfile(username: string): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.apiUrl}/users/${username}/`);
  }

  toggleFollow(username: string): Observable<{ message: string; is_following: boolean }> {
    return this.http.post<{ message: string; is_following: boolean }>(
      `${this.apiUrl}/users/${username}/follow/`, {}
    );
  }

  uploadAvatar(file: File): Observable<{ message: string; avatar: string | null }> {
    const formData = new FormData();
    formData.append('avatar', file);
    return this.http.post<{ message: string; avatar: string | null }>(
      `${this.apiUrl}/profile/avatar/`, formData
    );
  }

  removeAvatar(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/profile/avatar/`);
  }
}
