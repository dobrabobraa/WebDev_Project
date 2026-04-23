import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  username = '';
  password = '';
  errorMessage = '';

  constructor(private authService: AuthService, private router: Router) {}

  login(): void {
    this.errorMessage = '';
    this.authService.login(this.username, this.password).subscribe({
      next: () => this.router.navigate(['/feed']),
      error: err => {
        this.errorMessage = err.error?.non_field_errors?.[0] || err.error?.detail || 'Login failed.';
      }
    });
  }

  register(): void {
    this.errorMessage = '';
    this.authService.register(this.username, this.password).subscribe({
      next: () => this.login(),
      error: err => {
        this.errorMessage = err.error?.username?.[0] || 'Registration failed.';
      }
    });
  }
}
