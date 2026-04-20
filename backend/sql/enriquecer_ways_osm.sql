ALTER TABLE ways
ADD COLUMN IF NOT EXISTS osm_tag_key text,
ADD COLUMN IF NOT EXISTS osm_tag_value text;

UPDATE ways w
SET
    osm_tag_key = c.tag_key,
    osm_tag_value = c.tag_value
FROM configuration c
WHERE w.tag_id = c.tag_id;
