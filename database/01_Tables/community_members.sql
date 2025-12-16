CREATE TABLE CommunityMembers (
    community_id INT REFERENCES Communities(community_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    role_id INT REFERENCES Roles(role_id),
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (community_id, user_id)
);