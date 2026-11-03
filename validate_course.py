"""Validate depth, stable links, executable syntax and downloadable materials."""
import collections
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'dist/course.json').read_text())
assert data['edition']==2
assert len(data['modules'])==20 and len(data['lessons'])==80
ids=[l['id'] for l in data['lessons']]
assert len(set(ids))==80
assert ids==[f'{m:02d}-{n:02d}' for m in range(1,21) for n in range(1,5)]
assert all(n==4 for n in collections.Counter(l['module'] for l in data['lessons']).values())
questions=fences=cases=0
for l in data['lessons']:
 ident=l['id']
 assert len(l['goals'])>=3 and len(l['checks'])>=4 and len(l['pitfalls'])>=3,ident
 words=len((l['theory']+' '+l['practice']).split())
 assert words >= (750 if l['module']<=14 else 850),(ident,words)
 assert l['wordCount']==words
 assert len(re.findall(r'^#{2,4} ',l['theory'],re.M))>=3,ident
 assert all(key in data['sources'] for key in l['sources']),ident
 assert l['minutes']>=120,ident
 assert len(l['case']['prompt'].split())>=20,ident
 assert len(l['case']['answer'].split())>=80,ident
 cases+=1
 assert len(l['quiz']) >= (4 if l['module']<=14 else 6),ident
 for q in l['quiz']:
  assert 0<=q['answer']<len(q['options']) and len(set(q['options']))==len(q['options'])
  assert len(q['explanation'])>30
  questions+=1
 for field,text in [('theory',l['theory']),('practice',l['practice']),('case',l['case']['prompt']),('solution',l['case']['answer'])]:
  assert text.count('```')%2==0,(ident,field)
  assert not re.search(r'\bTODO\b|Lorem ipsum|скоро появится',text,re.I)
  for lang,code in re.findall(r'```([^\n]*)\n([\s\S]*?)```',text):
   fences+=1
   if lang=='xml':ET.fromstring('<root>'+code+'</root>')
   elif lang=='json':json.loads(code)
   elif lang in ('python','py'):compile(code,ident,'exec')
   elif lang in ('bash','sh'):
    result=subprocess.run(['bash','-n'],input=code,text=True,capture_output=True)
    assert result.returncode==0,(ident,result.stderr)
for x in data['glossary']:assert x['lesson'] in ids
for title,url in data['sources'].values():assert title and url.startswith('https://'),(title,url)
assert len(data['labScenarios'])==5
for c in data['labScenarios']:
 assert c['lesson'] in ids and len(c['tasks'])==5 and len(c['events'])>=8
 for e in c['events']:
  assert 0<=e['level']<=16 and re.fullmatch(r'\d{2}:\d{2}:\d{2}',e['time']) and e['timestamp'].endswith('Z')
app=(root/'dist/app.js').read_text()
for target in re.findall(r'#/lesson/(\d\d-\d\d)',app):assert target in ids,target
assert questions==386,questions
assert len(data['glossary'])==85 and cases==80
assert sum(l['wordCount'] for l in data['lessons'])>=65000
assert (root/'dist/wazuh-learning-plan-ru.md').stat().st_size>500000
assert (root/'dist/wazuh-course-complete-ru.md').stat().st_size>1500000
with zipfile.ZipFile(root/'dist/wazuh-lab-pack.zip') as z:
 assert z.testzip() is None and len(z.namelist())>=8
 assert not any(n.startswith('/') or '..' in Path(n).parts for n in z.namelist())
print(json.dumps(dict(modules=20,lessons=80,questions=questions,cases=cases,validated_code_blocks=fences,glossary=85,words=sum(l['wordCount'] for l in data['lessons']),hours=sum(l['minutes'] for l in data['lessons'])/60),ensure_ascii=False))
