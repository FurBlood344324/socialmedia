-- Social Media Database Initialization Script
-- This script creates all tables and inserts initial data

-- ============================================
-- Drop existing tables (in reverse order of dependencies)
-- ============================================
DROP TABLE IF EXISTS Messages CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS PostLikes CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS CommunityMembers CASCADE;
DROP TABLE IF EXISTS Communities CASCADE;
DROP TABLE IF EXISTS Follows CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS FollowStatus CASCADE;
DROP TABLE IF EXISTS PrivacyTypes CASCADE;
DROP TABLE IF EXISTS Roles CASCADE;

-- ============================================
-- Create lookup/reference tables first
-- ============================================

-- Roles table (for community members)
CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL
);

-- Privacy types table
CREATE TABLE PrivacyTypes (
    privacy_id SERIAL PRIMARY KEY,
    privacy_name VARCHAR(20) UNIQUE NOT NULL
);

-- Follow status table
CREATE TABLE FollowStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL
);

-- ============================================
-- Create main entity tables
-- ============================================

-- Users table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    bio TEXT,
    profile_picture_url TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Communities table
CREATE TABLE Communities (
    community_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    creator_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    privacy_id INT REFERENCES PrivacyTypes(privacy_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Create relationship/junction tables
-- ============================================

-- Community members table (junction)
CREATE TABLE CommunityMembers (
    community_id INT REFERENCES Communities(community_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    role_id INT REFERENCES Roles(role_id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (community_id, user_id)
);

-- Follows table (junction)
CREATE TABLE Follows (
    follower_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    following_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    status_id INT REFERENCES FollowStatus(status_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id)
);

-- ============================================
-- Create content tables
-- ============================================

-- Posts table
CREATE TABLE Posts (
    post_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    community_id INT REFERENCES Communities(community_id),
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE Comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INT REFERENCES Posts(post_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Post likes table
CREATE TABLE PostLikes (
    post_id INT REFERENCES Posts(post_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id)
);

-- Messages table
CREATE TABLE Messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    receiver_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    content TEXT,
    media_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Insert initial/seed data
-- ============================================

-- Insert default roles for communities
INSERT INTO Roles (role_name) VALUES 
    ('admin'),
    ('moderator'),
    ('member')
ON CONFLICT (role_name) DO NOTHING;

-- Insert privacy types
INSERT INTO PrivacyTypes (privacy_name) VALUES 
    ('public'),
    ('private')
ON CONFLICT (privacy_name) DO NOTHING;

-- Insert follow status types
INSERT INTO FollowStatus (status_name) VALUES 
    ('pending'),
    ('accepted'),
    ('rejected')
ON CONFLICT (status_name) DO NOTHING;

-- ============================================
-- Create indexes for better performance
-- ============================================

-- Index on users
CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);

-- Index on posts
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON Posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_community_id ON Posts(community_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON Posts(created_at DESC);

-- Index on comments
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON Comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON Comments(user_id);

-- Index on post likes
CREATE INDEX IF NOT EXISTS idx_postlikes_post_id ON PostLikes(post_id);
CREATE INDEX IF NOT EXISTS idx_postlikes_user_id ON PostLikes(user_id);

-- Index on follows
CREATE INDEX IF NOT EXISTS idx_follows_follower_id ON Follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following_id ON Follows(following_id);

-- Index on messages
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON Messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver_id ON Messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON Messages(created_at DESC);

-- Index on community members
CREATE INDEX IF NOT EXISTS idx_community_members_user_id ON CommunityMembers(user_id);
