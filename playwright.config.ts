import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests',
 testMatch:'**/*.e2e.spec.ts',
 timeout:45000,
 retries:process.env.CI?1:0,
 reporter:[['list'],['html',{open:'never'}]],
 use:{baseURL:'http://127.0.0.1:4173',trace:'retain-on-failure',screenshot:'only-on-failure',headless:true},
 webServer:{
   command:'npm run dev -- --host 127.0.0.1 --port 4173',
   url:'http://127.0.0.1:4173/webgis-educacao-canoas/',
   reuseExistingServer:!process.env.CI,
   timeout:45000
 }
});
