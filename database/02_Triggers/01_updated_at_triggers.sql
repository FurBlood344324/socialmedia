-- Trigger functions to automatically update updated_at timestamps
-- These will be executed BEFORE UPDATE operations

-- Generic function for updating updated_at column
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- Trigger for Posts table
CREATE TRIGGER update_posts_updated_at
    BEFORE UPDATE ON Posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for Users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON Users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for Comments table
CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON Comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
