#!/usr/bin/env python3
"""Behaviour checks for the on-device progress store (app/src/main/assets/nk-store.js).

The store holds the app's only copy of study progress, so the behaviours that
protect it are checked here against the shipped file, in a browser-shaped
harness with a small in-memory IndexedDB:

- restore points taken before a reset, restore or migration survive for the
  full two-week window, not only the first twelve,
- storage usage is reportable when a heavy value is null,
- a restore freezes the store, so a later flush commits nothing,
- a corrupt save announces no revision to other tabs.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "app/src/main/assets/nk-store.js"

HARNESS = r"""
const assert=require('assert'),fs=require('fs');
const SOURCE=fs.readFileSync(process.argv[2],'utf8');

// --- a minimal in-memory IndexedDB -----------------------------------------
function makeDb(){
  const stores={kv:new Map(),snapshotMeta:new Map(),snapshotData:new Map()};
  let metaId=100000;
  let kvWrites=0;
  const makeTx=names=>{
    // A transaction completes only after every request it issued has answered,
    // exactly like IndexedDB.
    const tx={oncomplete:null,onerror:null,onabort:null,pending:0,failed:false};
    const request=value=>{
      const r={onsuccess:null,onerror:null,result:value};
      tx.pending++;
      r._fire=()=>setTimeout(()=>{
        tx.pending--;
        if(r.onsuccess)r.onsuccess({target:{result:r.result}});
        if(tx.pending<=0&&!tx.settled)settle();
      },0);
      return r;
    };
    const settle=()=>{
      if(tx.settled)return;
      tx.settled=true;
      // A transaction can be made to fail on demand, to model a write error.
      if(db.failTxMatching&&db.failTxMatching(names)){db.failTxMatching=null;if(tx.onerror)tx.onerror({target:{error:new Error('write failed')}});return;}
      if(tx.oncomplete)tx.oncomplete();
    };
    const makeStore=name=>{
      const data=stores[name];
      const all=()=>[...data.values()];
      const keys=()=>[...data.keys()];
      return {
        getAll:()=>{const r=request(all());r._fire();return r;},
        getAllKeys:()=>{const r=request(keys());r._fire();return r;},
        get:key=>{const r=request(data.get(key));r._fire();return r;},
        put:(value,key)=>{if(name==='kv')kvWrites++;data.set(key,value);const r=request(key);r._fire();return r;},
        delete:key=>{data.delete(key);const r=request(undefined);r._fire();return r;},
        add:value=>{const key=value.id!=null?value.id:metaId++;data.set(key,{...value,id:key});const r=request(key);r._fire();return r;},
        index:()=>({openCursor:()=>{const rows=all().sort((a,b)=>(b.at||0)-(a.at||0));const r=request(rows.length?{value:rows[0],continue:()=>{}}:null);r._fire();return r;}}),
      };
    };
    tx.objectStore=makeStore;
    setTimeout(()=>{if(tx.pending<=0)settle();},0);
    return tx;
  };
  return {stores,makeTx,failTxMatching:null,kvWrites:()=>kvWrites};
}
const db=makeDb();
global.indexedDB={open:()=>{
  const request={onupgradeneeded:null,onsuccess:null,onerror:null,onblocked:null,
    result:{close(){},createObjectStore:()=>({createIndex:()=>({})}),
            transaction:(names)=>db.makeTx(names)}};
  // The store assigns onsuccess after open() returns, so fire it later.
  setTimeout(()=>{if(request.onsuccess)request.onsuccess({});},0);
  return request;
}};

// --- browser shape ----------------------------------------------------------
const localData={};
const localStorage={get length(){return Object.keys(localData).length;},key:i=>Object.keys(localData)[i],
  getItem:k=>Object.hasOwn(localData,k)?localData[k]:null,setItem:(k,v)=>{localData[k]=String(v);},removeItem:k=>{delete localData[k];},clear:()=>{}};
global.localStorage=localStorage;
global.Storage=function(){};
global.Storage.prototype=localStorage;
const posted=[];
global.BroadcastChannel=function(){this.postMessage=m=>posted.push(m);this.close=()=>{};};
const storageEstimate=()=>Promise.resolve({usage:10,quota:100});
Object.defineProperty(global,'navigator',{value:{storage:{estimate:storageEstimate,persisted:()=>Promise.resolve(false)}},writable:true,configurable:true});
global.sessionStorage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
global.location={reload:()=>{},href:'http://x/'};
global.document={getElementById:()=>null,createElement:()=>({style:{},classList:{add(){},remove(){}},setAttribute(){},appendChild(){}}),body:{appendChild(){}},addEventListener(){}};
global.window=global;
global.CustomEvent=function(){};global.StorageEvent=function(){};
global.addEventListener=()=>{};

// --- the store's own starting point ----------------------------------------
// A primary state in IndexedDB, plus a heavy key whose value is null: a
// migrated localStorage entry can hold one, and usage() must not choke on it.
db.stores.kv.set('qbank_state_v1',JSON.stringify({stateRevision:1,bookmarks:{}}));
db.stores.kv.set('qbank_state_lkg_v2',null);

eval(SOURCE);
const Store=global.window.NKStore;
assert(Store,'the store must publish window.NKStore');
const KEY='qbank_state_v1';
const wallClock=Date.now();

(async()=>{
// --- 1. manual restore points survive the whole two-week window -------------
await Store.ready;
const meta=db.stores.snapshotMeta;
let nextId=1;
const point=(reason,ageDays)=>{const at=wallClock-ageDays*864e5;const id=nextId++;meta.set(id,{id,at,reason,bytes:1});return id;};
for(let i=0;i<20;i++)point('manual',i%10);
for(let i=0;i<20;i++)point('auto',i%10);
// Pruning runs after a snapshot; take one to trigger it.
await Store.snapshot('trigger');
await new Promise(r=>setTimeout(r,40));
const kept=[...meta.values()].filter(m=>m.reason==='manual');
assert(kept.length===20,'every manual restore point inside two weeks must survive, kept '+kept.length);
const keptAuto=[...meta.values()].filter(m=>m.reason==='auto');
assert(keptAuto.length<=12+14,'automatic points must stay capped, kept '+keptAuto.length);

// --- 2. usage() tolerates a null heavy value -------------------------------
const usage=await Store.usage();
assert(typeof usage.progressBytes==='number','usage must report progress bytes');
assert(usage.progressBytes>=0,'usage bytes must not be negative');

// --- 3. a restore freezes the store, so a later flush commits nothing ------
await Store.snapshot('before-restore');
const points=await Store.snapshots();
assert(points.length>0,'the store must keep restore points');
// A restore whose own write fails leaves the pending batch queued; the store
// freezes anyway, so that batch must never be committed afterwards.
db.failTxMatching=names=>names.includes('kv')&&names.includes('snapshotMeta');
await Store.restore(points[0].id).catch(()=>{});
await new Promise(r=>setTimeout(r,40));
const writesBefore=db.kvWrites();
await Store.flush();
await new Promise(r=>setTimeout(r,40));
assert(db.kvWrites()===writesBefore,'a flush after a restore must not commit the frozen store');

// --- 4. a corrupt save announces no revision -------------------------------
posted.length=0;
localStorage.setItem(KEY,'{broken');
await new Promise(r=>setTimeout(r,60));
assert(!posted.some(m=>m&&m.type==='state'&&Number(m.revision)<0),
  'a corrupt save must not announce a negative revision: '+JSON.stringify(posted));

console.log('PROGRESS_STORE_BEHAVIOR_OK checks=4');
})().catch(error=>{console.error('PROGRESS_STORE_BEHAVIOR_FAIL:',error&&error.message);process.exit(1);});
"""


def main() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(HARNESS)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script), str(STORE)], check=True)
    finally:
        script.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
