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
   const municipal=page.getByText('Escolas no Censo Escolar',{exact:true});
   await expect(municipal).toBeVisible();
   await expect(page.getByText('68.490',{exact:true}).first()).toBeVisible();
   await expect(page.getByText('Registros de escolas no arquivo')).toBeVisible();
   await expect(page.getByText('Escolas com coordenadas')).toBeVisible();

   const skip=page.getByRole('link',{name:'Ir ao conteúdo principal'});
   await expect(skip).toHaveAttribute('href','#main-content');
   const nav=width<940?page.locator('#mobile-drawer'):page.locator('.sidebar');
   const go=async(section:string)=>{
    if(width<940){
     await page.locator('#open-nav').click();
     const button=nav.locator('[data-page="'+section+'"]');
     const group=button.locator('xpath=ancestor::section[contains(@class,"nav-group")]');
     if(await group.count()){
      const toggle=group.locator('[data-nav-group]');
      if(await toggle.getAttribute('aria-expanded')==='false')await toggle.click();
     }
     await expect(button).toBeVisible();
     await button.click();
     await expect(page.locator('#mobile-drawer')).toBeHidden();
    }else{
     const button=nav.locator('[data-page="'+section+'"]');
     const group=button.locator('xpath=ancestor::section[contains(@class,"nav-group")]');
     if(await group.count()){
      const toggle=group.locator('[data-nav-group]');
      if(await toggle.getAttribute('aria-expanded')==='false')await toggle.click();
     }
     await button.click();
    }
   };
   if(width<940){
     for(const section of ['sources','finance','quality','schools','municipal']){
       await go(section);
       await page.locator('#open-nav').click();
       const active=nav.locator('[data-page="'+section+'"]');
       await expect(active).toHaveClass(/active/);
       await expect(active).toHaveAttribute('aria-current','page');
       await expect(active).toBeVisible();
       await expect(active).toBeInViewport();
       await page.keyboard.press('Escape');
       await expect(page.locator('#mobile-drawer')).toBeHidden();
       await expect(page.locator('#open-nav')).toBeFocused();
     }
   }
   await go('schools');
   await expect(page.getByRole('heading',{name:'Escolas e território'})).toBeVisible();
   await expect(page.locator('.school-row').first()).toBeVisible();
   await page.locator('#stage-select').selectOption({label:'Educação Infantil'});
   expect(await page.locator('.school-row').count()).toBeGreaterThan(0);
   await page.locator('#stage-select').selectOption({label:'Todas'});
   await expect(page.locator('#size-select')).toBeVisible();
   // Busca filtra durante digitação e preserva foco ao redesenhar a lista.
   await page.locator('#school-search').fill('43198910');
   await expect(page.locator('.school-row')).toHaveCount(1,{timeout:10000});
   await expect(page.locator('#school-search')).toBeFocused();
   await page.locator('#school-search').fill('');
   await expect(page.locator('.school-row').first()).toBeVisible();
   await page.locator('.school-row').first().click();
   await expect(page.locator('#school-detail')).toBeVisible();
   await expect(page.getByText('PDDE 2025').first()).toBeVisible();

   await expect(page).toHaveURL(/inep=\d{8}/);
   await page.screenshot({path:testInfo.outputPath(device+'-ficha.png'),fullPage:true});
   // Os painéis não podem inferir indicadores municipais como dados escolares.

   await go('enrollments');
   await expect(page.locator('main h2').filter({hasText:'Rede escolar e matrículas'})).toBeVisible();
   await expect(page.locator('#rs-enrollments-chart')).toBeVisible();
   await go('infrastructure');
   await expect(page.locator('main h2').filter({hasText:'Infraestrutura escolar'})).toBeVisible();
   await go('quality');
   await expect(page.getByRole('heading',{name:'Qualidade e aprendizagem'})).toBeVisible();
   await expect(page.getByText('IDEB 2025 — anos iniciais')).toBeVisible();
   await expect(page.getByText('SAEB 2025 · rede ESTADUAL em Canoas')).toBeVisible();
   await expect(page.locator('#quality-chart')).toBeVisible();
   await expect(page.locator('#school-flow-chart')).toBeVisible();
   await expect(page.getByText('Nível socioeconômico (INSE) · referência 2023')).toBeVisible();
   await go('teachers');
   await expect(page.getByRole('heading',{name:'Docentes e formação adequada'})).toBeVisible();
   await expect(page.locator('#teacher-chart')).toBeVisible();
   await page.screenshot({path:testInfo.outputPath(device+'-docentes.png'),fullPage:true});
   await go('quality');

   await page.screenshot({path:testInfo.outputPath(device+'-ideb.png'),fullPage:true});
   await go('childhood');
   await expect(page.getByRole('heading',{name:'Educação infantil e demografia territorial'})).toBeVisible();
   await expect(page.getByText('Crianças de 0–3 anos')).toBeVisible();
   await expect(page.locator('#age-chart')).toBeVisible();
   await page.screenshot({path:testInfo.outputPath(device+'-infancia.png'),fullPage:true});
   await go('finance');
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
   await go('sources');
   await expect(page.getByText('Organizações e plataformas de apoio')).toBeVisible();
   await expect(page.getByText('INEP · Indicadores Educacionais')).toBeVisible();
   if(width<940){
     // Alternar tema refaz o DOM, mas não deve perder o destaque/posição.
     const lastItem=nav.locator('[data-page="sources"]');
     await expect(lastItem).toHaveAttribute('aria-current','page');
   }
   await page.screenshot({path:testInfo.outputPath(device+'-fontes.png'),fullPage:true});
   await page.locator('#theme').click();
   await expect(page.locator('html')).toHaveClass(/dark/);
   await page.screenshot({path:testInfo.outputPath(device+'-escuro.png'),fullPage:true});
   expect(errors,'Erros não tratados no navegador').toEqual([]);
  });
 });
}
