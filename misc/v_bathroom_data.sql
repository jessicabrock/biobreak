
/* generic view of data needed for the biobreak app */
CREATE OR REPLACE VIEW v_bathroom_data AS
SELECT    b.bathroom_id, b.name, b.unisex, b.accessible, b.changing_table,
          l.street, l.city, l.state, l.country, l.lnglat, l.latitude,
          l.longitude, l.directions, c.comment, r.user_id, r.score
FROM      bathrooms as b
LEFT JOIN      locations as l
    ON (b.bathroom_id = l.bathroom_id)
LEFT JOIN      comments as c
    ON (c.bathroom_id = l.bathroom_id)
LEFT JOIN      ratings as r
    ON (r.bathroom_id = l.bathroom_id)
WHERE b.active = true ;
