"""Optional Chromium smoke test. Install playwright separately; no network is used.

CHROMIUM_PATH can select a local browser. Uses page.set_content for environments
whose managed browser policy disables file URLs; the HTML has no external assets.
"""
from pathlib import Path
import json,os,shutil,hashlib

def main():
 from playwright.sync_api import sync_playwright
 root=Path(__file__).resolve().parents[1];html=(root/'web/visualizer.html').read_text()
 with sync_playwright() as p:
  exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
  kwargs={'headless':True}
  if exe:kwargs['executable_path']=exe
  browser=p.chromium.launch(**kwargs);page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];requests=[]
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
  page.set_content(html,wait_until='load');assert page.title().startswith('Search laboratory')
  assert not page.locator('#hhead').is_visible()
  page.locator('#next').click();assert page.evaluate('LAB.state().index')>=0
  page.locator('#reset').click();assert page.evaluate('LAB.state().index')==-1
  for a,c,wrong,expected in [('lazy','main',False,8),('eager','main',False,8),('astar','main',False,8),('astar','reopening',False,5),('astar','reopening',True,6),('astar','overestimate',False,11)]:
   page.evaluate('([a,c,w])=>LAB.select(a,c,w)',[a,c,wrong]);page.evaluate('LAB.finish()')
   assert page.evaluate('LAB.state().result.distance')==expected
   assert 'Returned cost '+str(expected) in page.locator('#result').inner_text()
   assert page.locator('#next').is_disabled()
  page.evaluate("LAB.select('lazy','main');LAB.jump('stale')");assert page.evaluate('LAB.state().event.stats.stale_pops')==1
  page.locator('#queueview').select_option('heap');assert page.locator('#qindex').inner_text()=='Index'
  opts=page.locator('#bookmark option').all_text_contents();assert 'First stale skip' in opts
  page.evaluate("LAB.select('eager','main');LAB.jump('decrease')");page.locator('#queueview').select_option('heap');assert 'position[node]' in page.locator('#queue').inner_text()
  page.evaluate("LAB.select('astar','reopening');LAB.jump('reopen')");assert page.locator('#hhead').is_visible()
  assert page.evaluate('LAB.state().event.stats.reexpansions')==1
  for size in [(1440,1000),(1280,800)]:
   page.set_viewport_size({'width':size[0],'height':size[1]})
   dims=page.evaluate("[document.querySelector('.controls').getBoundingClientRect().top, document.querySelector('.state').getBoundingClientRect().bottom, document.querySelector('.codepanel').getBoundingClientRect().bottom]")
   assert dims[0]>=max(dims[1:])-1,('Overlapping controls',dims)
  page.evaluate("LAB.select('eager','all');LAB.finish()");assert 'All reachable' in page.locator('#result').inner_text()
  assert not errors,errors
  assert not requests,requests
  browser.close()
 out={'status':'passed','browser':'Chromium','checks':'controls, all algorithms, deliberate failures, stale/reopen events, heap view, heuristic reveal, responsive non-overlap, no network requests','page_errors':errors,'external_requests':requests,'loading':'self-contained HTML via set_content','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'execution_context':'Optional browser test, separate from build_all and its CI validation'}
 (root/'results/browser_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
