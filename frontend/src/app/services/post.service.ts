import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Post } from '../models/post';

export interface CreatePostInput {
  title: string;
  text: string;
  hashtags: string[];
  mediaFiles?: File[];
  pollQuestion?: string;
  pollOptions?: string[];
}

@Injectable({ providedIn: 'root' })
export class PostService {
  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getPosts(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.apiUrl}/posts/`);
  }

  getPost(postId: number): Observable<Post> {
    return this.http.get<Post>(`${this.apiUrl}/posts/${postId}/`);
  }

  createPost(input: CreatePostInput): Observable<Post> {
    const fd = new FormData();
    fd.append('title', input.title);
    fd.append('text', input.text);
    if (input.hashtags && input.hashtags.length) {
      fd.append('hashtags_input_text', input.hashtags.join(' '));
    }
    if (input.pollQuestion && input.pollOptions && input.pollOptions.length >= 2) {
      fd.append('poll_question', input.pollQuestion);
      fd.append('poll_options_text', input.pollOptions.join('\n'));
    }
    (input.mediaFiles || []).forEach(f => fd.append('media_files', f, f.name));
    return this.http.post<Post>(`${this.apiUrl}/posts/`, fd);
  }

  updatePost(postId: number, title: string, text: string, hashtags: string[]): Observable<Post> {
    // JSON PATCH — edits don't involve files or polls
    return this.http.put<Post>(`${this.apiUrl}/posts/${postId}/`, {
      title, text, hashtags_input: hashtags,
    });
  }

  deletePost(postId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/posts/${postId}/`);
  }

  likePost(postId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/posts/${postId}/like/`, {});
  }

  addComment(postId: number, text: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/posts/${postId}/comments/`, { text });
  }

  votePoll(postId: number, optionId: number): Observable<{ message: string; my_vote_option_id: number | null }> {
    return this.http.post<{ message: string; my_vote_option_id: number | null }>(
      `${this.apiUrl}/posts/${postId}/vote/`,
      { option_id: optionId }
    );
  }
}
