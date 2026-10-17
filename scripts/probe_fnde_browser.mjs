import {chromium} from 'playwright';
const browser=await chromium.launch({headless:true});
for (const id of [82,56]){
 const page=await browser.newPage({acceptDownloads:false});
 const base='https://www.fnde.gov.br/plataforma-antonieta-de-barros/dados/produtos-de-dados/visualizar/'+id;
 console.log('PAGE',id);
 page.on('request',req=>{const url=req.url();if(url.includes('plataforma-antonieta-de-barros-api'))console.log('REQUEST',req.method(),url.slice(0,450),(req.postData()||'').slice(0,500));});
 page.on('response',res=>{const url=res.url();if(url.includes('plataforma-antonieta-de-barros-api'))console.log('RESPONSE',res.status(),url.slice(0,450),res.headers()['content-type']||'',res.headers()['content-length']||'');});
 page.on('download',async down=>{console.log('DOWNLOAD',down.url().slice(0,600),down.suggestedFilename());await down.cancel();});
 try{
  await page.goto(base,{waitUntil:'domcontentloaded',timeout:35000});
  const b=page.getByRole('button',{name:/Exportar artefato/i});
  await b.waitFor({timeout:15000});console.log('BUTTON',await b.count());
  await b.first().click({timeout:10000});
  await page.waitForTimeout(9000);
 }catch(err){console.log('BROWSER_ERROR',String(err).slice(0,350));}
 await page.close();
}
await browser.close();
