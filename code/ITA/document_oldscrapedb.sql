CREATE EXTENSION IF NOT EXISTS tablefunc;

WITH doc_role_name AS (
    SELECT *
    FROM crosstab(
                 '
                 SELECT document_id,
                        "role",
                        "name"
                 FROM document_detail
                 ',
                 '
                 SELECT DISTINCT "role"
                 FROM document_detail
                 ORDER BY 1
                 '
             ) AS ct( -- TODO: List dynamically?
                     document_id INT,
                     annulment_committee_members VARCHAR,
                     annulment_committee_president VARCHAR,
                     arbitrator VARCHAR,
                     claimant_appointee VARCHAR,
                     claimant_counsel VARCHAR,
                     claimant_expert VARCHAR,
                     country VARCHAR,
                     judge VARCHAR,
                     other_counsel VARCHAR,
                     other_expert VARCHAR,
                     president VARCHAR,
                     respondent_appointee VARCHAR,
                     respondent_counsel VARCHAR,
                     respondent_expert VARCHAR
        )
),
     doc_filtered AS (
         SELECT doc.id    document_id,
                url,
                doc.title,
                "date",
                dis.title dispute_title,
                dt.name   "document_type.name"
         FROM "document" doc,
              dispute dis,
              document_type dt,
              document_document_type ddt
         WHERE ddt.document_type_id IN (1, 3, 4, 8)
           AND doc.dispute_id = dis.id
           AND ddt.document_type_id = dt.id
           AND ddt.document_id = doc.id
     )
SELECT *
FROM doc_filtered
         LEFT JOIN doc_role_name
                   USING (document_id);
