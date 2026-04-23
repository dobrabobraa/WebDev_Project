import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { UserProfile } from '../../models/user-profile';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html'
})
export class ProfileComponent implements OnInit, OnDestroy {
  profile: UserProfile | null = null;
  loading = false;
  errorMessage = '';
  uploading = false;
  routeSub: Subscription | null = null;

  constructor(
    public authService: AuthService,
    private userService: UserService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.routeSub = this.route.paramMap.subscribe(params => {
      const urlUsername = params.get('username');
      const selfUsername = localStorage.getItem('username');
      const target = urlUsername || selfUsername;
      if (!target) {
        // Not logged in and no username in URL — just stop; template shows "not logged in".
        this.profile = null;
        return;
      }
      this.loadProfile(target);
    });
  }

  ngOnDestroy(): void {
    this.routeSub?.unsubscribe();
  }

  loadProfile(username: string): void {
    this.loading = true;
    this.errorMessage = '';
    this.userService.getProfile(username).subscribe({
      next: data => {
        this.profile = data;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to load profile.';
        this.profile = null;
        this.loading = false;
      }
    });
  }

  getInitial(): string {
    const name = this.profile?.username || '';
    return name.charAt(0).toUpperCase() || '?';
  }

  onAvatarSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files && input.files[0];
    if (!file || !this.profile) return;
    this.uploading = true;
    this.userService.uploadAvatar(file).subscribe({
      next: res => {
        if (this.profile) {
          this.profile.avatar = res.avatar;
        }
        this.uploading = false;
        input.value = '';
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Failed to upload avatar.';
        this.uploading = false;
        input.value = '';
      }
    });
  }

  removeAvatar(): void {
    if (!this.profile || !this.profile.avatar) return;
    this.uploading = true;
    this.userService.removeAvatar().subscribe({
      next: () => {
        if (this.profile) this.profile.avatar = null;
        this.uploading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to remove avatar.';
        this.uploading = false;
      }
    });
  }

  toggleFollow(): void {
    if (!this.profile) return;
    const username = this.profile.username;
    this.userService.toggleFollow(username).subscribe({
      next: res => {
        if (!this.profile) return;
        const wasFollowing = this.profile.is_following;
        this.profile.is_following = res.is_following;
        // Update followers count locally
        if (res.is_following && !wasFollowing) {
          this.profile.followers_count += 1;
        } else if (!res.is_following && wasFollowing) {
          this.profile.followers_count = Math.max(0, this.profile.followers_count - 1);
        }
      },
      error: err => {
        this.errorMessage = err?.error?.detail || 'Follow failed.';
      }
    });
  }

  logout(): void {
    this.authService.logout().subscribe({
      next: () => { this.authService.clearTokens(); window.location.href = '/login'; },
      error: () => { this.authService.clearTokens(); window.location.href = '/login'; }
    });
  }
}
