// Headless verification in an isolated browser, without using the user's tabs.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {pathToFileURL}=require('node:url');

(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1120}});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    // file:// plus blocked network proves the delivered pages work offline.
    await page.route(/^https?:\/\//,route=>route.abort());
    const base=path.resolve(__dirname,'../web');
    await page.goto(pathToFileURL(path.join(base,'experiments.html')).href);
    await page.waitForFunction(()=>window.FIELDLAB);
    const scenarios=await page.evaluate(()=>FIELDLAB.data.scenarios.map(s=>({name:s.case.name,renderer:s.case.renderer,keys:Object.keys(s.runs)})));
    let runs=0;
    for(let i=0;i<scenarios.length;i++){
      await page.locator('#scenario').selectOption(String(i));
      for(const key of scenarios[i].keys){
        await page.locator('#left-algo').selectOption(key);
        await page.locator('#step').click();
        await page.locator('#expand').click();
        await page.locator('#finish').click();
        const state=await page.evaluate(()=>({done:FIELDLAB.state().left.done,path:FIELDLAB.state().left.path,
          expected:FIELDLAB.data.scenarios[FIELDLAB.state().scenario].runs[document.getElementById('left-algo').value].result.path}));
        assert(state.done);
        assert.deepEqual(state.path,state.expected);
        runs++;
      }
      await page.locator('#heuristic').check();
      await page.locator('#overlay').uncheck();
      await page.locator('#code-toggle').check();
      await page.locator('#scrub').fill('2');
      await page.locator('#reset').click();
      await page.locator('#overlay').check();
      await page.locator('#code-toggle').uncheck();
    }
    const artifacts=path.resolve(__dirname,'../results/browser-checks');
    fs.mkdirSync(artifacts,{recursive:true});
    for(const renderer of ['grid','streets','game']){
      const index=scenarios.findIndex(s=>s.renderer===renderer);
      await page.locator('#scenario').selectOption(String(index));
      await page.locator('#heuristic').uncheck();
      await page.locator('#finish').click();
      await page.screenshot({path:path.join(artifacts,renderer+'.png'),fullPage:true});
    }
    // Verify the enemy advances along the computed route after search finishes.
    const before=await page.locator('#left-canvas').evaluate(c=>c.toDataURL());
    await page.waitForTimeout(350);
    const after=await page.locator('#left-canvas').evaluate(c=>c.toDataURL());
    assert.notEqual(before,after);
    await page.locator('#scenario').selectOption('0');
    await page.locator('#speed').selectOption('100');
    await page.locator('#play').click();
    await page.waitForFunction(()=>FIELDLAB.state().left.done&&FIELDLAB.state().right.done);
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:path.join(artifacts,'mobile.png'),fullPage:true});
    await page.setViewportSize({width:1440,height:1120});
    await page.goto(pathToFileURL(path.join(base,'benchmarks.html')).href);
    await page.waitForFunction(()=>window.BENCHMARKS);
    const total=await page.evaluate(()=>BENCHMARKS.data.length);
    assert.equal(await page.locator('#rows tr').count(),total);
    await page.locator('#family').selectOption('streets');
    assert((await page.locator('#rows tr').count())>0);
    await page.locator('#algorithm').selectOption('lazy');
    await page.locator('#sort').selectOption('runtime');
    assert.equal(await page.locator('#rows tr').count(),3);
    await page.locator('#family').selectOption('');
    await page.locator('#algorithm').selectOption('');
    await page.locator('#status').selectOption('timeout');
    assert.equal(await page.locator('#rows tr').count(),1);
    await page.locator('#status').selectOption('');
    await page.locator('#search').fill('Queue improvement');
    assert((await page.locator('#rows tr').count())>0);
    const broken=await page.locator('img').evaluateAll(images=>images.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
    assert.deepEqual(broken,[]);
    await page.screenshot({path:path.join(artifacts,'benchmarks.png'),fullPage:true});
    await page.goto(pathToFileURL(path.join(base,'visualizer.html')).href);
    await page.waitForFunction(()=>window.LAB);
    await page.locator('#case').selectOption('grid');
    await page.evaluate(()=>LAB.finish());
    assert.equal(await page.evaluate(()=>LAB.state().result.distance),33);
    assert.equal(await page.locator('#metrics').count(),0);
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(artifacts,'verification.json'),JSON.stringify({scenarios:scenarios.length,animation_runs:runs,
      benchmark_rows:total,offline:true,game_actor_moves:true,mobile_layout:true,legacy_visualizer:true,page_errors:errors},null,2)+'\n');
    console.log(`Browser checks passed: ${scenarios.length} scenes, ${runs} animation runs, ${total} benchmark rows; offline, mobile, gameplay and legacy viewer.`);
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
