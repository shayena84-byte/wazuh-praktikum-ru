"""Check that local assets work at the domain root and in a Pages subdirectory."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent / 'dist'

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ('src', 'href'):
            value = values.get(key)
            if value:
                self.urls.add(value)

parser = Assets()
parser.feed((ROOT / 'index.html').read_text())
app = (ROOT / 'app.js').read_text()
urls = set(parser.urls)
urls.update(match[1] for match in re.findall(r"fetch\(\s*(['\"])([^'\"]+)\1", app))
urls.update(re.findall(r'href="([^\"]+)"', app))
local = {
    url for url in urls
    if not url.startswith(('#', 'data:', 'http:', 'https:'))
    and '${' not in url
    and not re.fullmatch(r'\$\d+', url)
}
assert local, 'No local assets found'

for base in ('https://example.org/', 'https://example.github.io/wazuh-praktikum-ru/'):
    base_path = urlsplit(base).path
    for url in sorted(local):
        path = urlsplit(urljoin(base, url)).path
        assert path.startswith(base_path), f'Asset escapes Pages directory: {url}'
        asset = path[len(base_path):]
        assert (ROOT / asset).is_file(), f'Missing asset: {asset}'

print(f'Root and GitHub Pages paths verified: {len(local)} local asset references')
