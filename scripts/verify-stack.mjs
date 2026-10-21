import { strict as assert } from 'node:assert';
const base=process.env.API_URL||'http://localhost:5000';
const ai=process.env.AI_URL||'http://localhost:6000';
async function check(url,name){
  const r=await fetch(url); const t=await r.text(); assert(r.ok,`${name} returned ${r.status}: ${t}`); console.log(`PASS ${name}: ${t}`); return JSON.parse(t);
}
try {
  const api=await check(`${base}/api/health`,'API health');
  const a=await check(`${ai}/health`,'AI health');
  assert(api.status==='ok'); assert(a.status==='ok');
  console.log(a.imageModelLoaded ? 'PASS trained image model loaded' : 'WARN no trained image model loaded');
  console.log('Stack smoke test complete.');
} catch(e){ console.error(`FAIL ${e.message}`); process.exit(1); }
