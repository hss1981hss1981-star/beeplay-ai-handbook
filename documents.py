"""Expose published Office downloads as readable text without extra dependencies."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import html
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
S={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def extract(path):
 with ZipFile(path) as z:
  if path.suffix=='.docx':
   root=ET.fromstring(z.read('word/document.xml'))
   return '\n'.join(''.join(p.itertext()) if False else ''.join(t.text or '' for t in p.findall('.//w:t',W)) for p in root.findall('.//w:p',W))
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   shared=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',S)]
  wb=ET.fromstring(z.read('xl/workbook.xml'))
  rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  lines=[]
  for sheet in wb.findall('s:sheets/s:sheet',S):
   target=rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
   target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   lines.append('\n## '+sheet.get('name'))
   for row in ET.fromstring(z.read(target)).findall('.//s:row',S):
    cells=[]
    for c in row.findall('s:c',S):
     v=c.find('s:v',S);value=v.text if v is not None else ''
     if c.get('t')=='s':value=shared[int(value)] if value else ''
     elif c.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//s:t',S))
     cells.append(c.get('r')+': '+(value or '[blank / 待填写]'))
    lines.append(' | '.join(cells))
  return '\n'.join(lines)
def export_documents(out,target,prefix):
 links=[];texts=[]
 for path in sorted((out/'downloads').glob('*')):
  if path.suffix not in ('.docx','.xlsx'):continue
  text=extract(path);assert text.strip(),path
  name=path.name+'.txt';folder=out/'documents';folder.mkdir(exist_ok=True)
  (folder/name).write_text(text)
  links.append('<li><a href="'+prefix+'/documents/'+name+'">'+html.escape(path.name)+' — 全文 / Full text</a></li>')
  texts.append('# Download document: '+path.name+'\nSource: '+target+'/documents/'+name+'\n\n'+text)
 section='<h2>下载文档全文 / Downloaded document text</h2><ul>'+''.join(links)+'</ul>'
 for p in [out/'index.html',out/'read/index.html']:
  p.write_text(p.read_text().replace('</body>',section+'</body>'))
 with (out/'llms-full.txt').open('a') as f:f.write('\n\n'+'\n\n---\n\n'.join(texts))
 with (out/'llms.txt').open('a') as f:
  f.write('\n## Download document text\n')
  for p in sorted((out/'documents').glob('*.txt')):f.write('- ['+p.name+']('+target+'/documents/'+p.name+')\n')
 return len(texts)
