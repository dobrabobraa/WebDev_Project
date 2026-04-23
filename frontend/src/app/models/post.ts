export interface CommentItem {
  id: number;
  text: string;
  created_at: string;
  author_username: string;
  author_avatar?: string | null;
}

export interface PostMedia {
  id: number;
  kind: 'image' | 'video';
  url: string;
  order: number;
}

export interface PollOption {
  id: number;
  text: string;
  order: number;
  votes_count: number;
}

export interface Poll {
  id: number;
  question: string;
  options: PollOption[];
  total_votes: number;
  my_vote_option_id: number | null;
}

export interface Post {
  id: number;
  title: string;
  text: string;
  created_at: string;
  updated_at: string;
  hashtags: string[];
  author_username: string;
  author_avatar?: string | null;
  comments: CommentItem[];
  comments_count: number;
  likes_count: number;
  media: PostMedia[];
  poll: Poll | null;
}
