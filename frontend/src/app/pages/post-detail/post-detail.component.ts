import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Post, PollOption } from '../../models/post';
import { PostService } from '../../services/post.service';
import { AuthService } from '../../services/auth.service';
import { splitMentions, TextFragment } from '../../utils/mentions';

@Component({
  selector: 'app-post-detail',
  templateUrl: './post-detail.component.html'
})
export class PostDetailComponent implements OnInit, OnDestroy {
  post: Post | null = null;
  loading = false;
  errorMessage = '';
  commentDraft = '';
  routeSub: Subscription | null = null;

  // Edit mode
  isEditing = false;
  editTitle = '';
  editText = '';
  editHashtagsRaw = '';
  saving = false;

  // Poll
  votingOptionId: number | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private postService: PostService,
    public authService: AuthService,
  ) {}

  ngOnInit(): void {
    this.routeSub = this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      const id = idStr ? Number(idStr) : NaN;
      if (!id || Number.isNaN(id)) {
        this.errorMessage = 'Invalid post id.';
        return;
      }
      this.loadPost(id);
    });
  }

  ngOnDestroy(): void {
    this.routeSub?.unsubscribe();
  }

  loadPost(id: number): void {
    this.loading = true;
    this.errorMessage = '';
    this.postService.getPost(id).subscribe({
      next: data => { this.post = data; this.loading = false; },
      error: () => { this.errorMessage = 'Post not found.'; this.post = null; this.loading = false; }
    });
  }

  isMyPost(): boolean {
    const me = localStorage.getItem('username');
    return !!me && !!this.post && this.post.author_username === me;
  }

  // --- Mentions rendering ---
  renderFragments(text: string): TextFragment[] {
    return splitMentions(text || '');
  }

  // --- Poll ---
  percent(option: PollOption): number {
    if (!this.post?.poll || this.post.poll.total_votes === 0) return 0;
    return Math.round((option.votes_count / this.post.poll.total_votes) * 100);
  }

  vote(option: PollOption): void {
    if (!this.post) return;
    if (!this.authService.isLoggedIn()) {
      this.errorMessage = 'You need to login to vote.';
      return;
    }
    this.votingOptionId = option.id;
    this.postService.votePoll(this.post.id, option.id).subscribe({
      next: () => { this.votingOptionId = null; this.loadPost(this.post!.id); },
      error: () => { this.votingOptionId = null; this.errorMessage = 'Vote failed.'; }
    });
  }

  // --- Likes / comments / delete ---
  likePost(): void {
    if (!this.post) return;
    this.postService.likePost(this.post.id).subscribe({
      next: () => this.loadPost(this.post!.id),
      error: () => this.errorMessage = 'You need to login to like a post.'
    });
  }

  deletePost(): void {
    if (!this.post) return;
    this.postService.deletePost(this.post.id).subscribe({
      next: () => this.router.navigate(['/feed']),
      error: err => this.errorMessage = err?.error?.detail || 'Delete failed.'
    });
  }

  addComment(): void {
    if (!this.post) return;
    const text = this.commentDraft.trim();
    if (!text) return;
    this.postService.addComment(this.post.id, text).subscribe({
      next: () => { this.commentDraft = ''; this.loadPost(this.post!.id); },
      error: () => this.errorMessage = 'You need to login to comment.'
    });
  }

  // --- Edit ---
  parseHashtags(raw: string): string[] {
    return raw
      .split(/[\s,]+/)
      .map(t => t.trim().replace(/^#+/, '').toLowerCase())
      .filter(t => t.length > 0);
  }

  startEdit(): void {
    if (!this.post) return;
    this.editTitle = this.post.title;
    this.editText = this.post.text;
    this.editHashtagsRaw = (this.post.hashtags || []).map(t => '#' + t).join(' ');
    this.isEditing = true;
    this.errorMessage = '';
  }

  cancelEdit(): void {
    this.isEditing = false;
    this.errorMessage = '';
  }

  saveEdit(): void {
    if (!this.post) return;
    const title = this.editTitle.trim();
    const text = this.editText.trim();
    if (!title) { this.errorMessage = 'Title is required.'; return; }
    if (!text) { this.errorMessage = 'Post body is required.'; return; }
    this.saving = true;
    this.errorMessage = '';
    this.postService.updatePost(this.post.id, title, text, this.parseHashtags(this.editHashtagsRaw)).subscribe({
      next: updated => { this.post = updated; this.isEditing = false; this.saving = false; },
      error: err => { this.errorMessage = err?.error?.detail || 'Update failed.'; this.saving = false; }
    });
  }
}
