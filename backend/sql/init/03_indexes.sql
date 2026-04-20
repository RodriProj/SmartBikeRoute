-- Índices para acelerar as queries de custo por aresta no pgr_dijkstra.
-- Todas as queries do edge_cost_service filtram por osm_tag_key = 'highway'.

CREATE INDEX IF NOT EXISTS idx_ways_osm_tag_key
    ON ways (osm_tag_key);

CREATE INDEX IF NOT EXISTS idx_ways_osm_tag_value
    ON ways (osm_tag_value);

CREATE INDEX IF NOT EXISTS idx_ways_osm_tag_key_value
    ON ways (osm_tag_key, osm_tag_value);
