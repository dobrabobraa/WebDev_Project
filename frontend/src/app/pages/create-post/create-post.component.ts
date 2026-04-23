import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { PostService } from '../../services/post.service';

interface MediaPreview {
  file: File;
  url: string;
  kind: 'image' | 'video';
}

@Component({
  selector: 'app-create-post',
  templateUrl: './create-post.component.html'
})
export class CreatePostComponent {
  title = '';
  text = '';
  hashtagsRaw = '';
  errorMessage = '';
  saving = false;

  // Media
  mediaPreviews: MediaPreview[] = [];

  // Poll
  showPoll = false;
  pollQuestion = '';
  pollOptionsRaw = '';

  constructor(private postService: PostService, private router: Router) {}

  parseHashtags(): string[] {
    return this.hashtagsRaw
      .split(/[\s,]+/)
      .map(t => t.trim().replace(/^#+/, '').toLowerCase())
      .filter(t => t.length > 0);
  }

  parsePollOptions(): string[] {
    return this.pollOptionsRaw
      .split(/\r?\n/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;
    for (let i = 0; i < input.files.length; i++) {
      const file = input.files[i];
      const kind: 'image' | 'video' = file.type.startsWith('video/') ? 'video' : 'image';
      this.mediaPreviews.push({
        file,
        url: URL.createObjectURL(file),
        kind,
      });
    }
    input.value = '';
  }

  removeMedia(i: number): void {
    const item = this.mediaPreviews[i];
    if (item) URL.revokeObjectURL(item.url);
    this.mediaPreviews.splice(i, 1);
  }

  togglePoll(): void {
    this.showPoll = !this.showPoll;
    if (!this.showPoll) {
      this.pollQuestion = '';
      this.pollOptionsRaw = '';
    }
  }

  createPost(): void {
    if (this.saving) return;
    this.errorMessage = '';
    const title = this.title.trim();
    const text = this.text.trim();
    if (!title) { this.errorMessage = 'Title is required.'; return; }
    if (!text) { this.errorMessage = 'Post body is required.'; return; }

    let pollQuestion = '';
    let pollOptions: string[] = [];
    if (this.showPoll) {
      pollQuestion = this.pollQuestion.trim();
      pollOptions = this.parsePollOptions();
      if (pollQuestion && pollOptions.length < 2) {
        this.errorMessage = 'A poll needs at least 2 options.';
        return;
      }
      if (!pollQuestion && pollOptions.length > 0) {
        this.errorMessage = 'Poll question is required when options are set.';
        return;
      }
    }

    this.saving = true;
    this.postService.createPost({
      title,
      text,
      hashtags: this.parseHashtags(),
      mediaFiles: this.mediaPreviews.map(m => m.file),
      pollQuestion,
      pollOptions,
    }).subscribe({
      next: () => {
        this.mediaPreviews.forEach(m => URL.revokeObjectURL(m.url));
        this.router.navigate(['/feed']);
      },
      error: err => {
        this.errorMessage = err?.error?.title?.[0]
          || err?.error?.text?.[0]
          || 'Create post failed. Please login and try again.';
        this.saving = false;
      }
    });
  }
}
