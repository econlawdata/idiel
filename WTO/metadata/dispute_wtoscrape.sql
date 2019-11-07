CREATE EXTENSION IF NOT EXISTS tablefunc;

WITH dispute_role_country_list AS (
    SELECT *
    FROM crosstab(
                 '
                 SELECT dispute_id,
                        r.role,
                        array_to_string(array_agg(DISTINCT c.iso3), '','') c_iso3
                 FROM dispute_country dc,
                      country c,
                      "role" r
                 WHERE dc.country_id = c.id AND
                       dc.role = r.id
                 GROUP BY dispute_id,
                          r.role
                 ',
                 '
                 SELECT DISTINCT r.role
                 FROM "role" r
                 ORDER BY 1
                 '
             ) AS ct(
                     dispute_id INT,
                     claimant VARCHAR,
                     respondent VARCHAR,
                     third_party VARCHAR
        )
),
     dispute_agreement_dolcode_list AS (
         SELECT d.id                                                dispute_id,
                array_to_string(array_agg(DISTINCT a.dolcode), ',') dolcode
         FROM dispute d,
              agreement a,
              dispute_cited_agreement dca
         WHERE dca.dispute_id = d.id
           AND dca.agreement_id = a.id
         GROUP BY d.id
     )
SELECT d.id,
       d.code,
       title,
       short_title,
       reports_adopted,
       update_date,
       start_date,
       status_date,
       st.description   status_description,
       st.name          status_name,
       drcl.third_party "Country[Third_Party]",
       drcl.respondent  "Country[Respondent]",
       drcl.claimant    "Country[Claimant]",
       dadl.dolcode     dolcode,
       sj.name          subject_name
FROM dispute d,
     status st,
     subject sj,
     dispute_role_country_list drcl,
     dispute_agreement_dolcode_list dadl,
     dispute_subject dsj
WHERE d.status_id = st.id
  AND drcl.dispute_id = d.id
  AND dadl.dispute_id = d.id
  AND dsj.dispute_id = d.id
  AND dsj.subject_id = sj.id
