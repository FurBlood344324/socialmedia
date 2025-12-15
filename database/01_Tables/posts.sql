CREATE TABLE Posts (
    post_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    community_id INT REFERENCES Communities(community_id) ON DELETE CASCADE ON UPDATE CASCADE,
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_posts_content_or_media CHECK ((content IS NOT NULL AND content != '') OR (media_url IS NOT NULL AND media_url != ''))
);