-- Enriquece a tabela ways com colunas osm_tag_key e osm_tag_value
-- a partir da tabela configuration (gerada pelo osm2pgrouting).
-- Idempotente: colunas criadas com IF NOT EXISTS;
-- UPDATE só actualiza linhas onde o valor é realmente diferente.

ALTER TABLE ways
    ADD COLUMN IF NOT EXISTS osm_tag_key   text,
    ADD COLUMN IF NOT EXISTS osm_tag_value text;

UPDATE ways w
SET
    osm_tag_key   = c.tag_key,
    osm_tag_value = c.tag_value
FROM configuration c
WHERE w.tag_id = c.tag_id
  AND (
      w.osm_tag_key   IS DISTINCT FROM c.tag_key
   OR w.osm_tag_value IS DISTINCT FROM c.tag_value
  );
