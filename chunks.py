from pathlib import Path
import html,json,hashlib

def export_chunks(out,target,prefix):
 folder=out/'chunks';folder.mkdir(exist_ok=True)
 sources=[out/'llms-full.zh.txt',out/'llms-full.en.txt']+sorted((out/'documents').glob('*.txt'))
 manifest=[];directory=[]
 def page(title,body):return '<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{max-width:950px;margin:24px auto;padding:0 16px;font:16px/1.7 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#176a52}</style><body>'+body+'</body></html>'
 for n,source in enumerate(sources,1):
  text=source.read_text();remaining=text;parts=[]
  while remaining:
   cut=min(12000,len(remaining))
   if cut<len(remaining):
    line=remaining.rfind('\n',0,cut)
    if line>cut//2:cut=line+1
   parts.append(remaining[:cut]);remaining=remaining[cut:]
  assert ''.join(parts)==text
  links=[];records=[]
  for i,part in enumerate(parts,1):
   name=f'{n:02d}-{i:03d}.html';url=target+'/chunks/'+name
   nav='<p><a href="'+prefix+'/chunks/source-'+str(n)+'.html">本文件目录 / File index</a> · '+str(i)+' / '+str(len(parts))+'</p>'
   if i<len(parts):nav+='<a href="'+f'{n:02d}-{i+1:03d}.html'+'">下一段 / Next part</a>'
   title=source.name+' — '+str(i)+'/'+str(len(parts))
   (folder/name).write_text(page(title,'<h1>'+html.escape(title)+'</h1>'+nav+'<pre>'+html.escape(part)+'</pre>'+nav))
   sublinks=[];subrecords=[]
   for j,start in enumerate(range(0,len(part),4000),1):
    sub=part[start:start+4000];subname=f'{n:02d}-{i:03d}-{j:02d}.html';suburl=target+'/chunks/'+subname
    subtitle=title+' / subpart '+str(j)
    (folder/subname).write_text(page(subtitle,'<h1>'+html.escape(subtitle)+'</h1><pre>'+html.escape(sub)+'</pre><p>END OF SUBPART</p>'))
    sublinks.append('<li><a href="'+subname+'">'+html.escape(subtitle)+'</a></li>')
    subrecords.append({'url':suburl,'characters':len(sub),'sha256':hashlib.sha256(sub.encode()).hexdigest()})
   (folder/name).write_text(page(title,'<h1>'+html.escape(title)+'</h1>'+nav+'<p>若正文截断，请完整读取以下短段 / If truncated, read all subparts:</p><ol>'+''.join(sublinks)+'</ol><pre>'+html.escape(part)+'</pre>'+nav))
   links.append('<li><a href="'+name+'">'+html.escape(title)+'</a></li>')
   records.append({'part':i,'url':url,'subparts':subrecords,'characters':len(part),'sha256':hashlib.sha256(part.encode()).hexdigest()})
  source_url=target+'/chunks/source-'+str(n)+'.html'
  (folder/('source-'+str(n)+'.html')).write_text(page(source.name,'<a href="index.html">全部文件 / All files</a><h1>'+html.escape(source.name)+'</h1><p>共 '+str(len(parts))+' 段。请逐段读取并报告缺失段，目录不等于全文。 / Read every part and report missing parts.</p><ol>'+''.join(links)+'</ol>'))
  directory.append('<li><a href="source-'+str(n)+'.html">'+html.escape(source.name)+'</a> ('+str(len(parts))+' parts)</li>')
  manifest.append({'source':str(source.relative_to(out)),'index':source_url,'characters':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest(),'parts':records})
 total=sum(len(x['parts']) for x in manifest)
 (folder/'index.html').write_text(page('BeePlay 分段阅读 / Chunked reading','<h1>AI 分段阅读 / Chunked reading</h1><p>网页中英文全文及下载文档，共 '+str(total)+' 段，每段不超过 12,000 字符。请选择所需语言，按每份文件的目录逐段读取；说明实际覆盖范围，未读内容不可推断。 / Website text and Office documents, '+str(total)+' parts, at most 12,000 characters each. Choose a language, read each file in order, and report actual coverage.</p><ol>'+''.join(directory)+'</ol>'))
 (out/'reading-plan.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 for path in [out/'index.html',out/'read/index.html']:
  path.write_text(path.read_text().replace('<h1>','<p><a href="'+prefix+'/chunks/">AI 分段读取（推荐） / Chunked reading (recommended)</a></p><h1>',1))
 with (out/'llms.txt').open('a') as f:f.write('\n- [Recommended: complete chunked reading]('+target+'/chunks/)\n- [Reading coverage manifest]('+target+'/reading-plan.json)\n')
 return total
