"""Generate no-JavaScript reading copies from canonical bilingual content. Run before publishing."""
from pathlib import Path
import json,re,html
from html.parser import HTMLParser
from urllib.parse import urljoin
root=Path(__file__).resolve().parents[1]/'dist'
base='https://beeplay-product-map.hss1981hss1981.chatgpt.site'
class Text(HTMLParser):
 def __init__(self): super().__init__();self.parts=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t in ('p','div','section','article','tr','h1','h2','h3','h4','li','br'):self.parts.append('\n')
  if t=='td' or t=='th':self.parts.append(' | ')
  if t=='a' and a.get('href'): self.parts.append(' ['+urljoin(base+'/',a['href'])+'] ')
  if t=='img':self.parts.append(' '+a.get('alt','')+' ['+urljoin(base+'/',a.get('src',''))+'] ')
 def handle_data(self,d):self.parts.append(d)
 def text(self):return re.sub(r'\n[ \t]*\n+', '\n\n',''.join(self.parts)).strip()
def plain(s):
 p=Text();p.feed(s);return p.text()
def shell(title,body,lang):return '<!doctype html><html lang="'+lang+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow"><title>'+html.escape(title)+'</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:17px/1.7 system-ui;color:#24312b}a{color:#176a52}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #ccc;padding:8px}img,svg{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}details>*{display:revert}</style><body><nav><a href="/read/">全文目录 / Reading index</a> · <a href="/">交互网站 / Interactive site</a></nav>'+body+'</body></html>'
read=root/'read';read.mkdir(exist_ok=True)
urls=[base+'/',base+'/read/'];index=[];full=[]
for lang,filename in [('zh','content.json'),('en','content.en.json')]:
 data=json.loads((root/filename).read_text());pages=data['pages'];ids={p['id'] for p in pages}
 folder=read/lang;folder.mkdir(exist_ok=True);sections=[];links=[]
 for p in pages:
  body=p['body']
  def fix(m):
   target=m[2];ident=target[1:].split('?')[0]
   return m[1]+('/read/'+lang+'/'+ident+'.html' if ident in ids else '/?lang='+lang+target)+m[3]
  body=re.sub(r'(href=[\"\'])(#[^\"\']+)([\"\'])',fix,body)
  body=re.sub(r'(<details\b)(?![^>]*\bopen)([^>]*>)',r'\1 open\2',body)
  body=re.sub(r'((?:src|href)=[\"\'])(downloads/)',r'\1/\2',body)
  article='<h1>'+html.escape(p['title'])+'</h1><p>'+html.escape(p.get('lead',''))+'</p>'+body
  (folder/(p['id']+'.html')).write_text(shell(p['title'],article,lang))
  url=base+'/read/'+lang+'/'+p['id']+'.html';urls.append(url)
  links.append('<li><a href="'+url+'">'+html.escape(p['title'])+'</a></li>')
  sections.append('# '+p['title']+'\nID: '+p['id']+'\nSource: '+url+'\n'+p.get('lead','')+'\n\n'+plain(body))
 text='BeePlay — '+lang+' — content version '+str(data['version'])+'\nCurrent public handbook, including any explicitly marked historical/archive content. Historical text does not override current rules.\n\n'+'\n\n---\n\n'.join(sections)
 (root/('llms-full.'+lang+'.txt')).write_text(text)
 full.append(text);index.append('<h2>'+('中文' if lang=='zh' else 'English')+'</h2><p><a href="/llms-full.'+lang+'.txt">完整纯文本 / Complete plain text</a> · <a href="/'+filename+'">JSON</a></p><ul>'+''.join(links)+'</ul>')
# Include the complete definitions used by the clickable reference popovers.
ref=(root/'reference-data.js').read_text()
dec=json.JSONDecoder(); start=ref.index('?[',ref.index('window.HandbookReferenceData'))+1
en,n=dec.raw_decode(ref[start:]); rest=ref[start+n:].lstrip(); zh,_=dec.raw_decode(rest[1:].lstrip())
for lang,items in [('zh',zh),('en',en)]:
 appendix='\n\n# Reference popover definitions / 编号浮层释义\n'+json.dumps(items,ensure_ascii=False,indent=2)
 path=root/('llms-full.'+lang+'.txt');path.write_text(path.read_text()+appendix)
 full.append(appendix)
(root/'llms-full.txt').write_text('\n\n'.join(full))
(read/'index.html').write_text(shell('BeePlay · 全文读取 / Full-text access','<h1>BeePlay · 全文读取 / Full-text access</h1><p>以下内容与网站使用同一份数据生成，无需 JavaScript。章节内保留原有规则、表格和下载链接。<br>Generated from the same source as the website. No JavaScript required; rules, tables and download links are preserved.</p><p><a href="/llms-full.txt">中英文完整纯文本 / Complete bilingual text</a></p>'+''.join(index),'zh'))
(root/'llms.txt').write_text('# BeePlay product handbook\n\nPublic bilingual product requirements and team handoff. No login or JavaScript required at these URLs.\n\n- [Full bilingual text]('+base+'/llms-full.txt)\n- [Chinese text]('+base+'/llms-full.zh.txt)\n- [English text]('+base+'/llms-full.en.txt)\n- [All chapters and downloads]('+base+'/read/)\n- [Chinese canonical JSON]('+base+'/content.json)\n- [English canonical JSON]('+base+'/content.en.json)\n\nHistorical/archive material is labelled in the source and does not supersede current rules.\n')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+base+'/sitemap.xml\n')
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in urls)+'</urlset>')
p=root/'index.html';s=p.read_text();s=s.replace('</head>','<link rel="alternate" type="text/plain" href="/llms-full.txt" title="Complete bilingual handbook"><link rel="sitemap" href="/sitemap.xml"></head>') if '/llms-full.txt' not in s else s
s=re.sub(r'<noscript>.*?</noscript>','<noscript><a href="/read/">无需 JavaScript 阅读完整手册 / Read the complete handbook without JavaScript</a></noscript>',s,flags=re.S)
if 'AI / 全文读取' not in s:s=s.replace('</footer>','<a href="/read/">AI / 全文读取 · Full text</a></footer>')
p.write_text(s)
print('Generated',len(urls)-2,'static chapters; bilingual full text:',(root/'llms-full.txt').stat().st_size,'bytes')
