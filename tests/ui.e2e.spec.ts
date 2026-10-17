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
   await nav.locator('[data-page="finance"]').click();
   await expect(page.getByRole('heading',{name:'Financiamento público da educação'})).toBeVisible();
   await expect(page.getByText('Empenhado em 2025')).toBeVisible();
   await expect(page.locator('#finance-chart')).toBeVisible();
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
