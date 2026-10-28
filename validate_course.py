import collections, json, re, xml.etree.ElementTree as ET
from pathlib import Path

root=Path(__file__).resolve().parent
data=json.loads((root/'dist/course.json').read_text())
assert len(data['modules'])==14
assert len(data['lessons'])==56
ids={l['id'] for l in data['lessons']}
assert len(ids)==56
assert all(n==4 for n in collections.Counter(l['module'] for l in data['lessons']).values())
questions=0
fences=0
for l in data['lessons']:
    assert len(l['goals'])>=3 and len(l['checks'])>=3 and len(l['pitfalls'])>=3,l['id']
    assert len((l['theory']+' '+l['practice']).split())>=200,l['id']
    assert all(k in data['sources'] for k in l['sources']),l['id']
    assert l['minutes']>=60
    for q in l['quiz']:
        assert 0<=q['answer']<len(q['options']) and len(set(q['options']))==len(q['options'])
        assert len(q['explanation'])>20
        questions+=1
    for field in ['theory','practice']:
        text=l[field]
        assert text.count('```')%2==0,(l['id'],field)
        assert not re.search(r'\bTODO\b|Lorem ipsum|скоро появится',text,re.I)
        for lang, code in re.findall(r'```([^\n]*)\n([\s\S]*?)```',text):
            fences+=1
            if lang=='xml':
                ET.fromstring('<root>'+code+'</root>')
            if lang=='json':
                json.loads(code)
            if lang=='python':
                compile(code,l['id'],'exec')
for x in data['glossary']:
    assert x['lesson'] in ids,x
app=(root/'dist/app.js').read_text()
for target in re.findall(r'#/lesson/(\d\d-\d\d)',app):
    assert target in ids,target
assert questions==130,questions
assert (root/'dist/wazuh-learning-plan-ru.md').stat().st_size>50000
print(json.dumps({'modules':14,'lessons':56,'questions':questions,'validated_code_blocks':fences,'glossary':len(data['glossary']),'hours':sum(l['minutes'] for l in data['lessons'])/60},ensure_ascii=False))
