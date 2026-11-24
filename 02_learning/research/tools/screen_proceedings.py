"""Read-only primary-proceedings screening; no software/environment installation.

Title matches are discovery records, never eligibility or quality judgments.
PDF excerpts are local review aids, not a substitute for reading methods/results.
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r'adapt|fault|robust|recover|dynamics|embodiment|disturb|meta.?reinforcement|world.model|resilien|residual', re.I)
SOURCES = [f'https://proceedings.mlr.press/v{v}/' for v in (205,229,270,305)] + [f'https://www.roboticsproceedings.org/rss{v}/' for v in (19,20,21,22)]

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'RoboticsLiteratureReview/1.0'})
    return urllib.request.urlopen(req, timeout=40).read()

def clean(s):
    return html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()

def discover(url):
    s = get(url).decode('utf-8', errors='replace')
    rows = []
    if 'mlr.press' in url:
        for title, tail in re.findall(r'<p class="title">(.*?)</p>(.*?)(?=<div class="paper">|$)', s, re.S):
            title = clean(title)
            links = re.findall(r'href="([^"]+)"', tail)
            if PATTERN.search(title) and links:
                rows.append(dict(title=title, url=links[0], pdf=next((u for u in links if '.pdf' in u),None), source=url))
    else:
        for href, title in re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', s, re.S|re.I):
            title=clean(title)
            if PATTERN.search(title) and re.match(r'p\d+\.html$',href):
                page=urllib.parse.urljoin(url,href)
                rows.append(dict(title=title,url=page,pdf=page.replace('.html','.pdf'),source=url))
    return rows

def review_aid(row):
    row=dict(row)
    row['retrieved_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        page=get(row['url']).decode('utf-8',errors='replace')
        row['page_text']=clean(page)[:30000]
        if row.get('pdf'):
            doc=fitz.open(stream=get(row['pdf']),filetype='pdf')
            row['pages']=len(doc)
            paragraphs=[]
            for i,p in enumerate(doc):
                text=p.get_text()
                # First two pages plus local evidence around technical conditions.
                if i<2:
                    paragraphs.append({'page':i+1,'text':text[:14000]})
                else:
                    lines=text.splitlines()
                    hits=[j for j,line in enumerate(lines) if re.search(r'limitation|github|code availability|action space|observation space|mid.episode|within.episode|actuator fail|privileged|code is|coming soon',line,re.I)]
                    snippets=[' '.join(lines[max(0,j-2):min(len(lines),j+7)]) for j in hits]
                    if snippets: paragraphs.append({'page':i+1,'snippets':snippets})
            row['review_excerpts']=paragraphs
            joined='\n'.join(p.get_text() for p in doc)
            row['github_mentions']=sorted(set(re.findall(r'https?://github\.com/[\w.-]+/[\w.-]+',joined)))
        row['status']='retrieved; human eligibility assessment required'
    except Exception as e:
        row['status']='retrieval error: '+str(e)
    return row

if __name__=='__main__':
    catalog=[]
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        for url,result in zip(SOURCES,pool.map(discover,SOURCES)):
            catalog.extend(result)
            print(json.dumps({'source':url,'title_candidates':len(result)},ensure_ascii=False),flush=True)
    catalog=list({r['url']:r for r in catalog}.values())
    (ROOT/'evidence'/'proceedings_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    out=ROOT/'evidence'/'primary_review_aids.jsonl'
    with out.open('w',encoding='utf-8') as f, cf.ThreadPoolExecutor(max_workers=3) as pool:
        for i,row in enumerate(pool.map(review_aid,catalog)):
            f.write(json.dumps(row,ensure_ascii=False)+'\n'); f.flush()
            print(json.dumps({'done':i+1,'total':len(catalog),'title':row['title'],'status':row['status'],'github':row.get('github_mentions',[])},ensure_ascii=False),flush=True)
