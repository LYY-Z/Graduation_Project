"""Check source navigability, not scientific validity or reproduction success."""
import concurrent.futures as cf
import datetime as dt
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]

def check(url):
    row={'url':url,'checked_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    # HEAD does not download papers, models or datasets.
    req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'RoboticsLiteratureReview/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            row.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
    except urllib.error.HTTPError as e:
        row.update(status=e.code,error=str(e))
    except Exception as e:
        row.update(status=None,error=str(e))
    row['interpretation']='Navigability only. HEAD refusal/403/429/timeouts do not prove absence.'
    return row

if __name__=='__main__':
    urls=set()
    for path in ROOT.rglob('*.md'):
        text=path.read_text(encoding='utf-8')
        for url in re.findall(r'https?://[^\s<>\]\)"\u3002\uff0c]+',text):
            if not any(x in url for x in ('localhost','127.0.0.1')):
                urls.add(url.rstrip('.,;'))
    with (ROOT/'evidence'/'source_link_checks.jsonl').open('w',encoding='utf-8') as f,cf.ThreadPoolExecutor(max_workers=3) as pool:
        for i,row in enumerate(pool.map(check,sorted(urls))):
            f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
            print(json.dumps({'done':i+1,'total':len(urls),'url':row['url'],'http':row['status']}),flush=True)
