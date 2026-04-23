import { Component, OnInit } from '@angular/core';
import { Post } from '../../models/post';
import { PostService } from '../../services/post.service';

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html'
})
export class FeedComponent implements OnInit {
  posts: Post[] = [];
  errorMessage = '';

  constructor(private postService: PostService) {}

  ngOnInit(): void {
    this.loadPosts();
  }

  loadPosts(): void {
    this.postService.getPosts().subscribe({
      next: data => {
        this.posts = data;
        this.errorMessage = '';
      },
      error: () => {
        this.errorMessage = 'Failed to load posts.';
      }
    });
  }
}
