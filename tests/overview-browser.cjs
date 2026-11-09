const { chromium } = require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const path=require('node:path');
const http=require('node:http');
const root=path.resolve(process.argv[2] || 'public');
const graph=JSON.parse(fs.readFileSync(path.join(root,'overview/graph.json'),'utf8'));
const total=graph.nodes.length, pubs=graph.stats.publications, software=graph.stats.software;
const server=http.createServer((req,res)=>{
 const requestPath=decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/website(?=\/)/,'');
 let file=path.resolve(root,'.'+requestPath);
 if(!file.startsWith(root+path.sep) && file!==root){res.writeHead(403).end();return;}
 try{
  if(fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
  const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'};
  res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');
  res.end(fs.readFileSync(file));
 }catch{res.writeHead(404).end();}
});
const out=process.env.BROWSER_ARTIFACT_DIR;
let browser;
(async()=>{
 browser=await chromium.launch({headless:true});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base=`http://127.0.0.1:${server.address().port}/website/`;
 const results=[];
 for(const scenario of ['desktop','blocked-cdn','mobile','malformed-cache']){
  console.log('scenario',scenario);
  const context=await browser.newContext({viewport:scenario==='mobile'?{width:390,height:844}:{width:1440,height:1000}});
  await context.route('**/analytics.hellebo.de/**',route=>route.abort());
  if(scenario==='blocked-cdn') await context.route('**/unpkg.com/**',route=>route.abort());
  if(scenario==='malformed-cache') await context.addInitScript(()=>localStorage.setItem('ov-layout-v6','42'));
  const page=await context.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'overview/',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>!document.querySelector('#ov-search').disabled,{timeout:30000});
  assert.equal(await page.locator('#ov-stat-pub').innerText(),String(pubs));
  assert.equal(await page.locator('#ov-stat-sw').innerText(),String(software));
  assert.equal(await page.locator('#ov-results li').count(),total);
  assert.equal(await page.locator('#ov-results .ov-result-authors').count(),pubs);
  assert(await page.locator('#ov-results li').first().evaluate(e=>e.querySelector('p').getBoundingClientRect().top >= e.querySelector('a').getBoundingClientRect().bottom));
  assert.match(await page.locator('#ov-results li').first().innerText(),/Transplantation of LPS/);
  const preprint=page.locator('#ov-results li').filter({has:page.locator('a[href="https://doi.org/10.21203/rs.3.rs-10029339/v1"]')});
  assert.match(await preprint.innerText(),/Preprint · Research Square\. 2026/);
  await page.locator('#ov-search').fill('preprint');
  await page.waitForFunction(()=>document.querySelectorAll('#ov-results li').length===1);
  assert.match(await page.locator('#ov-results li').innerText(),/Serum copper and calcium/);
  await page.locator('#ov-search').press('Escape');
  await page.waitForFunction(n=>document.querySelectorAll('#ov-results li').length===n,total);

  if(scenario==='blocked-cdn') assert.match(await page.locator('#ov-loading').innerText(),/Search, filters/);
  await page.locator('#ov-search').fill('zzzz-no-matching-publication');
  await page.waitForFunction(()=>window.__ovSearchHits?.size===0);
  await page.waitForFunction(()=>document.querySelectorAll('#ov-results li').length===0);
  await page.locator('#ov-search').press('Escape');
  await page.waitForFunction(()=>window.__ovSearchHits===null);
  await page.waitForFunction(n=>document.querySelectorAll('#ov-results li').length===n, total);
  await page.getByRole('button',{name:`Publication · ${pubs}`,exact:true}).click();
  assert.equal(await page.locator('#ov-results li').count(),software);
  await page.reload({waitUntil:'networkidle'});
  await page.waitForFunction(n=>document.querySelectorAll('#ov-results li').length===n, software);
  await page.getByRole('button',{name:`Software · ${software}`,exact:true}).click();
  await page.reload({waitUntil:'networkidle'});
  await page.waitForFunction(()=>!document.querySelector('#ov-search').disabled);
  assert.equal(await page.locator('#ov-results li').count(),0);
  await page.getByRole('button',{name:'Reset all',exact:true}).click();
  assert.equal(await page.locator('#ov-results li').count(),total);
  const commaVenue=page.getByRole('button',{name:/Antioxidants \(Basel, Switz/});
  await commaVenue.click();
  const matching=await page.locator('#ov-results li').count();
  assert(matching<total && matching>software);
  await page.reload({waitUntil:'networkidle'});
  await page.waitForFunction(()=>!document.querySelector('#ov-search').disabled);
  assert.equal(await page.locator('#ov-results li').count(),matching);
  await page.getByRole('button',{name:'Reset all',exact:true}).click();
  if(out){fs.mkdirSync(out,{recursive:true}); await page.screenshot({path:`${out}/${scenario}.png`,fullPage:true});}
  assert.deepEqual(errors,[]);
  results.push({scenario,pageErrors:errors,overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
  await context.close();
 }
 const page=await browser.newPage();
 for(const route of ['','impressum/','privacy/','publications/']){
  const response=await page.goto(base+route);
  assert.equal(response.status(),200,route);
 }
 await browser.close();server.close();if(out)fs.writeFileSync(out+'/browser.json',JSON.stringify(results,null,2)+'\n');console.log(results);
})().catch(async e=>{console.error(e);if(browser) await browser.close();server.close();process.exitCode=1;});
