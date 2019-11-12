SELECT doc.*,
       dis.code  "dispute.code",
       dt.name   "doctype.name",
       rt.name   "document_reporttype.reporttype.name",
       prod.name "document_product.product.name",
       durl.url  "document_url.url"
FROM "document" doc,
     doctype dt,
     dispute dis,
     reporttype rt,
     product prod,
     document_doctype ddt,
     document_reporttype drt,
     document_url durl,
     document_product dprod,
     dispute_document dd
WHERE dt.id IN (4, 5, 7, 12)
  AND rt.id IN (1, 3, 4)
  AND durl.language = 0
  AND ddt.document_id = doc.id
  AND ddt.doctype_id = dt.id
  AND drt.document_id = doc.id
  AND drt.reporttype_id = rt.id
  AND durl.document_id = doc.id
  AND dprod.document_id = doc.id
  AND dprod.product_id = prod.id
  AND dd.dispute_id = dis.id
  AND dd.document_id = doc.id;
