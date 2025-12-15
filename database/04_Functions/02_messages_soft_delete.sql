CREATE OR REPLACE FUNCTION messages_sender_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL THEN
        NEW.sender_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION messages_receiver_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL THEN
        NEW.receiver_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
