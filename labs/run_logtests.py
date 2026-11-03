"""Run trusted, reviewed fixtures on an isolated Wazuh manager."""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BIN=Path("/var/ossec/bin/wazuh-logtest")
if not BIN.is_file():
    raise SystemExit("Wazuh logtest not installed: this is not a matching test result")
subprocess.run(["/var/ossec/bin/wazuh-analysisd","-t"],check=True,timeout=30)
cases=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
failed=[]
for case in cases:
    name=case["file"]
    if Path(name).name != name:
        raise ValueError("Fixture names must be plain filenames")
    path=(ROOT/"fixtures"/name).resolve()
    if path.parent != (ROOT/"fixtures").resolve():
        raise ValueError("Fixture path escapes fixtures directory")
    lines=path.read_text(encoding="utf-8").splitlines()
    if len(lines)!=1:
        raise ValueError(f"One JSON line required: {name}")
    json.loads(lines[0])
    expected=f'{case["rule"]}:{case["level"]}:{case["decoder"]}'
    result=subprocess.run([str(BIN),"-U",expected],input=lines[0]+"\n",
        text=True,capture_output=True,timeout=30,check=False)
    print(name,"PASS" if result.returncode==0 else "FAIL")
    if result.returncode:
        failed.append(name)
        print(result.stdout,result.stderr)
raise SystemExit(1 if failed else 0)
