export interface UserProfile {
  username: string;
  avatar: string | null;
  posts_count: number;
  likes_received: number;
  comments_count: number;
  followers_count: number;
  following_count: number;
  is_following: boolean;
  is_self: boolean;
}
