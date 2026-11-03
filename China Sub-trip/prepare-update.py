"""Integrate the destination guide without changing files outside this sub-trip."""
from pathlib import Path
import json, re, shutil

root=Path(__file__).parent
data_path=root/'destinations-data.js'
data_text=data_path.read_text(encoding='utf-8')
for place_id,url in {
    'ruili':'https://www.mlrdyl.cn/',
    'ximeng':'https://mz.yn.gov.cn/html/2026/huanjingmei_0202/4062556.html',
    'shaxi':'https://english.www.gov.cn/news/202503/18/content_WS67d91959c6d0868f4e8f0ee5.html',
}.items():
    data_text=re.sub(r"(id:'"+place_id+r"'.*?source:)('[^']+')",lambda m:m.group(1)+repr(url),data_text,flags=re.S)
data_path.write_text(data_text,encoding='utf-8')
options_path=root/'trip-options.js'
options_text=options_path.read_text(encoding='utf-8')
options_text=options_text.replace('let token;try{token=localStorage.getItem', 'let token=responseToken;try{token=token||localStorage.getItem')
options_text=options_text.replace('if(!token)token=crypto.randomUUID();try{localStorage.setItem', 'if(!token)token=crypto.randomUUID();responseToken=token;try{localStorage.setItem')
options_path.write_text(options_text,encoding='utf-8')
index=root/'index.html'
text=index.read_text(encoding='utf-8')
if 'trip-options.css' not in text:
    text=text.replace('<link rel="stylesheet" href="trip-theme.css">','<link rel="stylesheet" href="trip-theme.css">\n<link rel="stylesheet" href="trip-options.css">')
if '<script src="trip-options.js">' not in text:
    text=text.replace('<script src="translations.js"></script>','<script src="translations.js"></script>\n<script src="destinations-data.js"></script>\n<script src="photo-credits-data.js"></script>\n<script src="trip-options.js"></script>')
text=text.replace("const label=filter==='all'?t('all places'):t('{city} overnight / departure days',{city:t(filter.charAt(0).toUpperCase()+filter.slice(1))});", "const label=filter==='all'?t('all places'):t('{city} overnight / departure days',{city:window.YunnanCityLabel(filter)});")
text=re.sub(r"    const events=\[.*?\n    \];", "    const events=window.YunnanRouteEvents.map(e=>[e[0],e[1],e[2][i18n.language]||e[2].en,e[3][i18n.language]||e[3].en]);",text,flags=re.S)
text=text.replace('hotel+meals+activities+800+400','hotel+meals+activities+1200+600').replace("renderMoney('transport-total',800)","renderMoney('transport-total',1200)").replace("renderMoney('contingency-total',400)","renderMoney('contingency-total',600)").replace('{transport:800,contingency:400}','{transport:1200,contingency:600}')
index.write_text(text,encoding='utf-8')
credits=[]
for name in ['image-credits.json','destination-photo-credits.json']:
    credits.extend(json.loads((root/'assets'/name).read_text(encoding='utf-8-sig')))
(root/'photo-credits-data.js').write_text('window.YunnanPhotoCredits = '+json.dumps(credits,ensure_ascii=False)+';\n',encoding='utf-8')
public=root/'response-site'/'public'
trip=public/'trip'
trip.mkdir(parents=True,exist_ok=True)
for name in ['index.html','trip-theme.css','trip-options.css','translations.js','destinations-data.js','photo-credits-data.js','trip-options.js','Yunnan-itinerary.md','Sources.md','Image-credits.md']:
    shutil.copy2(root/name,trip/name)
shutil.copytree(root/'assets',trip/'assets',dirs_exist_ok=True)
hosted_index=trip/'index.html'
hosted_index.write_text(hosted_index.read_text(encoding='utf-8').replace('href="../winter-trip.html"','href="#route"'),encoding='utf-8')
# The wider personal trip is not part of this shareable group page.
unneeded_parent=public/'winter-trip.html'
if unneeded_parent.exists():
    unneeded_parent.unlink()
(root/'response-site'/'app'/'page.tsx').write_text("import { redirect } from 'next/navigation';\nexport default function Home() { redirect('/trip/index.html?lang=zh'); }\n",encoding='utf-8')
# PowerShell 5 writes UTF-8 with a BOM; JSON imports require plain UTF-8.
hosting=root/'response-site'/'.openai'/'hosting.json'
hosting.write_text(hosting.read_text(encoding='utf-8-sig'),encoding='utf-8')
print('Updated local page; prepared hosted trip with',len(credits),'credited photos.')
