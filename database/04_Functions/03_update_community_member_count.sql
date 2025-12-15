-- Member Count Update Trigger Function
-- Used by: POST /api/communities/<id>/join, POST /api/communities/<id>/leave
CREATE OR REPLACE FUNCTION update_community_member_count()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE Communities
        SET member_count = member_count + 1
        WHERE community_id = NEW.community_id;
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE Communities
        SET member_count = member_count - 1
        WHERE community_id = OLD.community_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
