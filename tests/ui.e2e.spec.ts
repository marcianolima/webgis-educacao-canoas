import {test,expect} from '@playwright/test';

for(const [device, width, height] of [
  ['desktop',1440,900], ['celular',390,844], ['tablet',810,1080],
] as const) {
 test.describe(device,()=>{
  test.use({viewport:{width,height}, reducedMotion:'reduce'});
  test('painel municipal e navegação escolar',async({page},testInfo)=>{
   const errors:string[]=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('/webgis-educacao-canoas/');
   await expect(page.getByRole('heading',{name:'Educação em Canoas'})).toBeVisible({timeout:20000});
   await expect(page.getByText('347.657',{exact:true})).toBeVisible();
   const municipal=page.getByText('Escolas georreferenciadas',{exact:true});
   await expect(municipal).toBeVisible();
   const nav=width<940?page.locator('.mobile-menu'):page.locator('.sidebar');
   await nav.locator('[data-page="schools"]').click();
   await expect(page.getByRole('heading',{name:'Escolas e território'})).toBeVisible();
   await expect(page.locator('.school-row').first()).toBeVisible();
   await page.locator('#stage-select').selectOption({label:'Educação Infantil'});
   expect(await page.locator('.school-row').count()).toBeGreaterThan(0);
   await page.locator('#stage-select').selectOption({label:'Todas'});
   await expect(page.locator('#size-select')).toBeVisible();
   await page.locator('.school-row').first().click();
   await expect(page.locator('#school-detail')).toBeVisible();
   await expect(page).toHaveURL(/inep=\d{8}/);
   await page.screenshot({path:testInfo.outputPath(device+'-ficha.png'),fullPage:true});
   // Os painéis não podem inferir indicadores municipais como dados escolares.
   await nav.locator('[data-page="quality"]').click();
   await expect(page.getByRole('heading',{name:'Qualidade e aprendizagem'})).toBeVisible();
   await expect(page.getByText('IDEB 2025 — anos iniciais')).toBeVisible();
   await expect(page.locator('#quality-chart')).toBeVisible();
   await page.screenshot({path:testInfo.outputPath(device+'-ideb.png'),fullPage:true});
   await nav.locator('[data-page="childhood"]').click();
   await expect(page.getByRole('heading',{name:'Educação infantil e demografia territorial'})).toBeVisible();
   await expect(page.getByText('Crianças de 0–3 anos')).toBeVisible();
   await expect(page.locator('#age-chart')).toBeVisible();
   await page.screenshot({path:testInfo.outputPath(device+'-infancia.png'),fullPage:true});
   await nav.locator('[data-page="finance"]').click();
   await expect(page.getByRole('heading',{name:'Financiamento público da educação'})).toBeVisible();
   await expect(page.getByText('Empenhado em 2025')).toBeVisible();
   await expect(page.locator('#finance-chart')).toBeVisible();
   await expect(page.getByText('PNAE · previsão de repasses por ação (2024)')).toBeVisible();
   await expect(page.getByText('PNAE · valores informados como repassados ao município')).toBeVisible();
   await expect(page.getByText('PNATE · valores a pagar (não pagamentos realizados)')).toBeVisible();
   // Regressão: cifras longas não podem ultrapassar as caixas nem a viewport móvel.
   const overflow=await page.locator('.finance-kpis .kpi-value').evaluateAll(els=>
    els.map(el=>{
      const box=el.getBoundingClientRect();
      const parent=el.closest('.kpi')?.getBoundingClientRect();
      return {value:el.textContent||'',withinCard:!!parent && box.left>=parent.left-1 && box.right<=parent.right+1,
        scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,viewport:window.innerWidth};
    })
   );
   expect(overflow.length).toBeGreaterThanOrEqual(4); // 4 estágios orçamentários + previsão PNAE quando disponível
   for(const m of overflow){
     expect(m.withinCard,m.value+' saiu do cartão').toBeTruthy();
     expect(m.scrollWidth,m.value+' excedeu o container').toBeLessThanOrEqual(m.clientWidth+1);
   }
   expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(width+1);

   await page.screenshot({path:testInfo.outputPath(device+'-financas.png'),fullPage:true});
   await nav.locator('[data-page="sources"]').click();
   await expect(page.getByText('Organizações e plataformas de apoio')).toBeVisible();
   await page.screenshot({path:testInfo.outputPath(device+'-fontes.png'),fullPage:true});
   await page.locator('#theme').click();
   await expect(page.locator('html')).toHaveClass(/dark/);
   await page.screenshot({path:testInfo.outputPath(device+'-escuro.png'),fullPage:true});
   expect(errors,'Erros não tratados no navegador').toEqual([]);
  });
 });
}
