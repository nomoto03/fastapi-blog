-- postsテーブル作成
CREATE TABLE posts (
  post_id serial PRIMARY KEY,
  title text NOT NULL,
  content text NOT NULL,
  image_url text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- tagsテーブル作成
CREATE TABLE tags (
  tag_id serial PRIMARY KEY,
  tag_name varchar(255) NOT NULL UNIQUE,
  color_code varchar(7),
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- blogsTagsテーブル作成
CREATE TABLE blogTags (
  post_id int REFERENCES posts(post_id),
  tag_id int REFERENCES tags(tag_id),
  PRIMARY KEY (post_id, tag_id)
);

