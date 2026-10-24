# BUG-01-003 — Restoring an account snapshot replaces this device's sync identity

- **Area:** 01 persistence & sync
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit bdd5d0c3
- **Files:** `app/src/main/modules/cross_device_sync.js:62`, `app/src/main/modules/cross_device_sync.js:66`
- **Introduced by:** unknown

## What happens

When an account that was previously used on another device is opened here, `nkRestoreAccountSnapshot` replaces the whole sync metadata, including `deviceId`. After that, this device uploads envelopes stamped with the other device's ID, so per-device conflict resolution and tombstones are attributed to the wrong device.

## Evidence

```js
function nkRestoreAccountSnapshot(snapshot){
  const nextState=nkNormalizeState(snapshot.state),nextMeta=nkNormalizeSyncMeta(snapshot.syncMeta);
  state=nextState;
  if(nkDurablePersist(state,'account switch')===false)throw new Error(...);
  nkSyncMeta=nextMeta;   // <-- deviceId comes from the snapshot
  ...
}
```

`nkSyncMeta.deviceId` is generated per device in `nkNormalizeSyncMeta` and is used as `ownerDevice` on every envelope (`nkEnvelope(..., ownerDevice: nkSyncMeta.deviceId, ...)`). `nkChooseWinner` breaks ties by `ownerDevice`. An adopted foreign ID therefore changes conflict outcomes.

## Learner impact

Cross-device merge/tie-breaking can favor the wrong copy after an account switch, and tombstones are attributed to a device that did not create them. Study progress is not directly lost, but merge correctness is compromised.

## Root cause

Account snapshots correctly carry the account's sync metadata, but `deviceId` is device-scoped, not account-scoped. Restore overwrites it instead of preserving the current device's identity.

## Proposed fix

```diff
--- a/app/src/main/modules/cross_device_sync.js
+++ b/app/src/main/modules/cross_device_sync.js
@@ -61,9 +61,15 @@
   }
   function nkRestoreAccountSnapshot(snapshot){
     const nextState=nkNormalizeState(snapshot.state),nextMeta=nkNormalizeSyncMeta(snapshot.syncMeta);
+    // This device keeps its own sync identity. A snapshot taken on another
+    // device must not make this device upload envelopes stamped with that
+    // device's ID, or per-device conflict resolution and tombstones are
+    // attributed to the wrong device.
+    const localDeviceId=(nkSyncMeta&&nkSyncMeta.deviceId)||nextMeta.deviceId;
     state=nextState;
     if(nkDurablePersist(state,'account switch')===false)throw new Error('Account progress could not be saved on this device.');
     nkSyncMeta=nextMeta;
+    nkSyncMeta.deviceId=localDeviceId;
     if(!nkSaveSyncMeta())throw new Error('Account sync history could not be saved on this device.');
     applySubject(SUBJECT_BY_NAME[snapshot.activeSubject]?snapshot.activeSubject:'Biochemistry');
     localStorage.removeItem(NK_PRE_CLOUD_BACKUP);
--- a/tools/test_cross_device_sync_v1.py
+++ b/tools/test_cross_device_sync_v1.py
@@ -422,6 +422,18 @@
   assert(state.fsrsPreferences.desiredRetention===0.9&&state.fsrsPreferences.dailyCap===200,'legacy payload must keep the whole-block merge');
   console.log('CROSS_DEVICE_SYNC_BEHAVIOR_OK');
 }
+// Restoring an account snapshot must not adopt the other device's identity:
+// this device keeps stamping its own envelopes, or per-device conflict
+// resolution and tombstones are attributed to the wrong device.
+nkSyncMeta=nkNormalizeSyncMeta({deviceId:'this-device',boundUid:'account-b'});
+const foreignSnapshot={uid:'account-b',activeSubject:'Biochemistry',
+  state:{attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}},
+  syncMeta:{deviceId:'other-device',boundUid:'account-b',outbox:{},localHashes:{},known:{},winners:{},cursors:{}}};
+nkRestoreAccountSnapshot(foreignSnapshot);
+assert(nkSyncMeta.deviceId==='this-device','restoring a snapshot must not adopt the other device identity');
+assert(nkEnvelope('bookmarks','q1',{active:true},1).ownerDevice==='this-device','this device must stamp its own envelopes');
+assert(nkSyncMeta.boundUid==='account-b','the restored account binding must be kept');
+
 testRequests().catch(error=>{console.error(error);process.exitCode=1;});
 '''
     prelude = r'''
```

## Verification

- Sign in on device A, sign out, sign in with an account whose snapshot was created on device B; confirm `nkSyncMeta.deviceId` is unchanged and still matches device A.
- Run `python3 tools/test_cross_device_sync_v1.py`.

## Alternatives considered

Preserving device ID in `nkSwitchLocalAccount` before writing the snapshot would also work, but restore is the single choke point used by both switch and recovery, so fixing it there covers both paths.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The finding is correct, but the proposed patch was a no-op and was reworked before being applied.

`nkRestoreAccountSnapshot` (cross_device_sync.js:62) replaces the whole sync metadata, including `deviceId`, and `nkEnvelope` stamps every upload with `nkSyncMeta.deviceId` as `ownerDevice`. A snapshot taken on another device therefore makes this device upload under the other device's identity, and the per-device conflict resolution and tombstones that depend on `ownerDevice` are attributed to the wrong device.

The patch as proposed inserted

```js
nkSyncMeta=nextMeta;
nextMeta.deviceId = (nkSyncMeta && nkSyncMeta.deviceId) || nextMeta.deviceId;
```

which assigns `nextMeta.deviceId` from itself: `nkSyncMeta` was already overwritten with `nextMeta` on the line above, so the expression is always `nextMeta.deviceId || nextMeta.deviceId` and the line changes nothing. The device identity would still have been adopted.

The applied patch takes the local identity before the metadata is replaced and puts it back afterwards:

```js
const localDeviceId=(nkSyncMeta&&nkSyncMeta.deviceId)||nextMeta.deviceId;
...
nkSyncMeta=nextMeta;
nkSyncMeta.deviceId=localDeviceId;
```

The fallback keeps the snapshot's own ID when this device has none yet, so a first sign-in still gets an identity.

`tools/test_cross_device_sync_v1.py` now restores a snapshot whose `syncMeta.deviceId` is `other-device` on a device whose identity is `this-device`, and asserts that the identity survives the restore, that the restored account binding is kept, and that an envelope created afterwards is stamped with this device's ID. On the pre-fix module it fails with "restoring a snapshot must not adopt the other device identity".
