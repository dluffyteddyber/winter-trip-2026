from pathlib import Path
import urllib.request, hashlib, zipfile, io

root = Path(__file__).parent / '.tools'
root.mkdir(exist_ok=True)
base = 'https://nodejs.org/dist/latest-v22.x/'
manifest = urllib.request.urlopen(base + 'SHASUMS256.txt', timeout=60).read().decode()
digest, filename = next(line.split() for line in manifest.splitlines() if line.endswith('-win-x64.zip'))
payload = urllib.request.urlopen(base + filename, timeout=120).read()
assert hashlib.sha256(payload).hexdigest() == digest
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in archive.namelist())
    archive.extractall(root)
print(root / filename.removesuffix('.zip') / 'node.exe')
