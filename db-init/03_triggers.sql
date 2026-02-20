-- Syncronize updated_at columns with current timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_samples_modtime
    BEFORE UPDATE ON public.samples
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();