from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlsplit,unquote
from concurrent.futures import ThreadPoolExecutor
import json,re,hashlib,datetime,subprocess,sys,shutil
SOURCE='https://beeplay-product-map.hss1981hss1981.chatgpt.site'
TARGET='https://hss1981hss1981-star.github.io/beeplay-ai-handbook'
PREFIX='/beeplay-ai-handbook'
out=Path('public');shutil.rmtree(out,ignore_errors=True);out.mkdir()
def fetch(path):
 local=Path('dist')/path
 if local.is_file():return local.read_bytes()
 with urlopen(Request(SOURCE+'/'+path,headers={'User-Agent':'BeePlay-Handbook-Sync/1.0'}),timeout=60) as r:return r.read()
def save(path,data):
 p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
shutil.rmtree('dist',ignore_errors=True)
Path('dist').mkdir()
for name in ['content.json','content.en.json','reference-data.js','index.html']:
 (Path('dist')/name).write_bytes(fetch(name))
subprocess.run([sys.executable,'scripts/build-readable.py'],check=True)
data={lang:fetch(name) for lang,name in [('zh','content.json'),('en','content.en.json')]}
assert len({json.loads(raw)['version'] for raw in data.values()})==1, 'Language versions differ; retry next run'
pages={lang:json.loads(raw)['pages'] for lang,raw in data.items()}
assert {p['id'] for p in pages['zh']}=={p['id'] for p in pages['en']}
paths=['read/index.html','llms.txt','llms-full.txt','llms-full.zh.txt','llms-full.en.txt','robots.txt','sitemap.xml']
paths += ['read/'+lang+'/'+p['id']+'.html' for lang in pages for p in pages[lang]]
assets=set()
files={}
with ThreadPoolExecutor(max_workers=6) as pool:
 for path,raw in zip(paths,pool.map(fetch,paths)):
  text=raw.decode()
  if path.endswith('.html'):
   assert '<html' in text
   for link in re.findall(r'(?:src|href)=[\"\']([^\"\']+)',text):
    u=urlsplit(urljoin(SOURCE+'/'+path,link))
    if u.netloc==urlsplit(SOURCE).netloc and u.path.startswith('/downloads/'):
     assets.add(unquote(u.path.lstrip('/')))
  files[path]=text
# Include each actual published download/image; abort the whole run on any failure.
with ThreadPoolExecutor(max_workers=6) as pool:
 for path,raw in zip(sorted(assets),pool.map(fetch,sorted(assets))):save(path,raw)
for path,text in files.items():
 text=text.replace(SOURCE+'/read/',TARGET+'/read/').replace(SOURCE+'/llms',TARGET+'/llms').replace(SOURCE+'/content',TARGET+'/content').replace(SOURCE+'/downloads/',TARGET+'/downloads/').replace(SOURCE+'/sitemap.xml',TARGET+'/sitemap.xml')
 if path.endswith('.html'):
  text=re.sub(r'((?:href|src)=[\"\'])/(read/|downloads/|llms|content)',lambda m:m[1]+PREFIX+'/'+m[2],text)
  text=text.replace('href="/"','href="'+SOURCE+'/"').replace('href="/?','href="'+SOURCE+'/?')
 save(path,text.encode())
for lang,raw in data.items():save('content'+('.en' if lang=='en' else '')+'.json',raw)
index=files['read/index.html'].replace(SOURCE+'/read/',TARGET+'/read/')
index=re.sub(r'((?:href|src)=[\"\'])/(read/|downloads/|llms|content)',lambda m:m[1]+PREFIX+'/'+m[2],index).replace('href="/"','href="'+SOURCE+'/"')
save('index.html',index.encode());save('.nojekyll',b'')
for lang,ps in pages.items():
 full=(out/('llms-full.'+lang+'.txt')).read_text()
 for p in ps:assert p['title'] in full, p['id']
manifest={'source':SOURCE,'source_versions':{l:json.loads(v)['version'] for l,v in data.items()},'synced_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'chapters':sum(map(len,pages.values())),'downloads':len(assets),'files':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}}
save('sync-status.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode())
print('Verified',manifest['chapters'],'chapters and',len(assets),'assets')
