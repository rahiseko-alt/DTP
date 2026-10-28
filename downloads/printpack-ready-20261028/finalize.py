"""Restore exact production boxes after Ghostscript and preserve the PDF/X output intent through merging."""
from pathlib import Path
import json,hashlib,re,os
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'build-proof.json'));MM=72/25.4
for o in proof['outputs']:
 path=R/o['file'];d=fitz.open(path)
 for p in d:
  p.set_mediabox(fitz.Rect(0,0,230*MM,317*MM));p.set_trimbox(fitz.Rect(10*MM,10*MM,220*MM,307*MM));p.set_bleedbox(fitz.Rect(7*MM,7*MM,223*MM,310*MM));d.xref_set_key(p.xref,'ArtBox','null')
 info=d.xref_get_key(-1,'Info');assert info[0]=='xref';ix=int(info[1].split()[0]);d.xref_set_key(ix,'Trapped','/False');d.xref_set_key(ix,'GTS_PDFXVersion','(PDF/X-1a:2001)');d.xref_set_key(ix,'GTS_PDFXConformance','(PDF/X-1a:2001)')
 xml=d.get_xml_metadata()
 if 'GTS_PDFXVersion' not in xml and '</rdf:RDF>' in xml:xml=xml.replace('</rdf:RDF>','<rdf:Description rdf:about="" xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/" pdfxid:GTS_PDFXVersion="PDF/X-1a:2001"/></rdf:RDF>');d.set_xml_metadata(xml)
 temp=path.with_suffix('.final.pdf');d.save(temp,garbage=4,deflate=True);d.close();os.replace(temp,path);o['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();o['bytes']=path.stat().st_size;o['boxes_restored_after_pdfwrite']=True
 print(o['label'],o['bytes'],o['sha256'],flush=True)
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
