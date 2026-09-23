/* Exercise the actual packaged Android WebView, including native Back/restart. */
const {_android: android}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

async function main(){
  const artifact=path.resolve('build/android-artifact');
  const apks=fs.readdirSync(artifact,{recursive:true}).filter(p=>p.endsWith('.apk'));
  assert.equal(apks.length,1,'exactly one candidate APK is required');
  const apk=path.join(artifact,apks[0]);
  const sdk=process.env.ANDROID_HOME||process.env.ANDROID_SDK_ROOT;
  const versions=fs.readdirSync(path.join(sdk,'build-tools')).sort().reverse();
  const aapt=versions.map(v=>path.join(sdk,'build-tools',v,'aapt')).find(p=>fs.existsSync(p));
  const badging=execFileSync(aapt,['dump','badging',apk],{encoding:'utf8'});
  const pkg=badging.match(/package: name='([^']+)'/)[1];
  assert(['com.qbank.marrowpilot','com.qbank.biochemistry'].includes(pkg));
  const [device]=await android.devices();assert(device,'Android emulator unavailable');
  const output='build/android-interaction';fs.mkdirSync(output,{recursive:true});
  await device.installApk(fs.readFileSync(apk));
  async function launch(){
    await device.shell(`am start -n ${pkg}/com.qbank.biochemistry.MainActivity`);
    const view=await device.webView({pkg,timeout:60000});
    const page=await view.page();page.setDefaultTimeout(30000);
    await page.waitForFunction(()=>location.hostname==='qbank.local'&&window.QB?.getState);
    return page;
  }
  // Android WebView updates a hash route in the current document. Playwright's
  // waitForURL defaults to a load event, which is not emitted for that change.
  async function waitForHash(page,hash){
    await page.waitForFunction(expected=>location.hash===expected,hash);
  }
  async function waitForDashboard(page){
    await page.waitForFunction(()=>(location.hash===''||location.hash==='#dashboard')&&Boolean(document.querySelector('button.nk-home-focus-action')));
  }
  const report=[];
  try{
    for(const [label,size,density] of [['phone','1080x2400',440],['tablet','1600x2560',320]]){
      await device.shell(`am force-stop ${pkg}`);
      await device.shell(`wm size ${size}`);await device.shell(`wm density ${density}`);
      await device.shell(`pm clear ${pkg}`);
      let page=await launch();
      await page.evaluate(()=>window.QB.startAllPractice());
      await page.waitForFunction(()=>window.QB.getState().activeSession?.questionIds.length>4);
      await page.locator('.option-list button').first().waitFor();
      const original=await page.evaluate(()=>window.QB.getState().activeSession);
      await page.locator('.option-list button').first().click();
      await page.waitForFunction(()=>window.QB.getState().activeSession.submitted[window.QB.getState().activeSession.questionIds[0]]);
      assert.equal(await page.locator('.option-list .correct').count(),1);
      await page.evaluate(id=>window.QB.toggleBookmark(id),original.questionIds[0]);
      await page.getByRole('button',{name:'Next',exact:true}).dblclick();
      assert.equal(await page.evaluate(()=>window.QB.getState().activeSession.index),1);
      await page.evaluate(()=>window.QB.openSessionReview());
      await page.locator('#nk-session-review').getByRole('button',{name:'Pause',exact:true}).click();
      const pauseState=await page.evaluate(()=>({url:location.href,hash:location.hash,lifecycle:window.QB.getState().activeSession?.lifecycle,index:window.QB.getState().activeSession?.index,reviewVisible:Boolean(document.querySelector('#nk-session-review')),bodyText:document.body.innerText.slice(0,300)}));
      fs.writeFileSync(`${output}/${label}-pause-state.json`,JSON.stringify(pauseState,null,2));
      console.log('ANDROID_PAUSE_STATE '+JSON.stringify(pauseState));
      await waitForHash(page,'#dashboard');
      await page.waitForFunction(()=>window.QB.getState().activeSession?.lifecycle==='paused'&&!document.querySelector('#nk-session-review'));
      await device.screenshot({path:`${output}/${label}-paused.png`});
      await device.shell(`am force-stop ${pkg}`);
      // Wait for the closed process to leave Playwright's WebView inventory.
      for(let i=0;i<40&&device.webViews().some(v=>v.pkg()===pkg);i++)await new Promise(resolve=>setTimeout(resolve,250));
      page=await launch();
      await page.locator('button.nk-home-focus-action').click();
      await page.waitForFunction(()=>window.QB.getState().activeSession?.lifecycle==='active');
      const resumed=await page.evaluate(()=>window.QB.getState().activeSession);
      assert.equal(resumed.id,original.id);assert.deepEqual(resumed.questionIds,original.questionIds);assert.equal(resumed.index,1);
      assert(await page.evaluate(id=>Boolean(window.QB.getState().bookmarks[id]),original.questionIds[0]));
      assert.equal(await page.evaluate(id=>window.QB.getState().attempts[id]?.length,original.questionIds[0]),1);
      // This invokes MainActivity.onBackPressed / WebView.goBack, not JS navigation.
      const backBefore=await page.evaluate(()=>({url:location.href,hash:location.hash,historyLength:history.length,lifecycle:window.QB.getState().activeSession?.lifecycle}));
      await device.shell('input keyevent KEYCODE_BACK');
      await waitForDashboard(page);
      const backAfter=await page.evaluate(()=>({url:location.href,hash:location.hash,historyLength:history.length,lifecycle:window.QB.getState().activeSession?.lifecycle,sessionId:window.QB.getState().activeSession?.id,index:window.QB.getState().activeSession?.index}));
      assert.notEqual(backAfter.hash,backBefore.hash);
      assert.equal(backAfter.sessionId,original.id);assert.equal(backAfter.index,1);
      const backEvidence={before:backBefore,after:backAfter};
      fs.writeFileSync(`${output}/${label}-back-state.json`,JSON.stringify(backEvidence,null,2));
      console.log('ANDROID_BACK_STATE '+JSON.stringify(backEvidence));
      await device.screenshot({path:`${output}/${label}-after-back.png`});
      await page.locator('button.nk-home-focus-action').click();
      await waitForHash(page,'#practice');
      await page.evaluate(()=>window.QB.openSessionReview());
      await page.locator('#nk-session-review').getByRole('button',{name:'Submit',exact:true}).dblclick();
      await page.waitForFunction(()=>!window.QB.getState().activeSession);
      assert.equal(await page.evaluate(id=>window.QB.getState().tests.filter(t=>t.id===`practice_${id}`).length,original.id),1);
      await page.getByRole('button',{name:'Review Solutions',exact:true}).click();
      await page.waitForFunction(()=>window.QB.getState().activeSession?.mode==='review');
      const before=await page.evaluate(()=>JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews]));
      await page.getByRole('button',{name:'Next',exact:true}).click();
      await page.getByRole('button',{name:'Previous',exact:true}).click();
      await page.locator('#cr-grid').click();
      await page.locator('#qb-question-navigator').getByRole('button',{name:'End Review',exact:true}).click();
      assert.equal(await page.evaluate(()=>JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews])),before);
      await page.evaluate(()=>window.QB.nav('dashboard'));
      await waitForHash(page,'#dashboard');
      await device.screenshot({path:`${output}/${label}-home.png`});
      report.push({device:label,size,density,viewport:await page.evaluate(()=>({width:innerWidth,height:innerHeight})),nativeBack:'PASS',forceStopResume:'PASS',practiceReviewFsrs:'PASS'});
      console.log('ANDROID_INTERACTION_VIEWPORT_OK '+JSON.stringify(report.at(-1)));
    }
    fs.writeFileSync(`${output}/report.json`,JSON.stringify(report,null,2));
    console.log('ANDROID_QUESTION_INTERACTION_OK');
  }finally{await device.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
