"""Static format checks. Does not execute the Wazuh engine."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
assert len(manifest)==6
assert len({x["file"] for x in manifest})==6
tree=ET.fromstring((ROOT/"course_auth_rules.xml").read_text(encoding="utf-8"))
ids=[x.attrib["id"] for x in tree.findall("rule")]
assert len(ids)==len(set(ids))
for case in manifest:
    assert Path(case["file"]).name==case["file"]
    path=ROOT/"fixtures"/case["file"]
    lines=path.read_text(encoding="utf-8").splitlines()
    assert len(lines)==1,path
    value=json.loads(lines[0])
    assert isinstance(value,dict) and value["app"]=="course-auth"
    assert str(case["rule"]) in ids
    print(case["file"],"FORMAT OK")
print("Static checks passed. Rule matching still requires Wazuh.")
