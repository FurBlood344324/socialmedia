-- Message Soft Delete Functions and Triggers

-- CREATE OR REPLACE FUNCTION messages_sender_soft_delete()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     IF NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL THEN
--         NEW.sender_deleted := TRUE;
--     END IF;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE OR REPLACE FUNCTION messages_receiver_soft_delete()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     IF NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL THEN
--         NEW.receiver_deleted := TRUE;
--     END IF;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- Used by: DELETE /api/messages/<id> (Note: Requires repository to perform UPDATE instead of DELETE)
CREATE TRIGGER messages_sender_soft_delete_trigger
BEFORE UPDATE OF sender_id ON Messages
FOR EACH ROW
WHEN (NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL)
EXECUTE FUNCTION messages_sender_soft_delete();

CREATE TRIGGER messages_receiver_soft_delete_trigger
BEFORE UPDATE OF receiver_id ON Messages
FOR EACH ROW
WHEN (NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL)
EXECUTE FUNCTION messages_receiver_soft_delete();
