# BUG-01-003 — Restoring an account snapshot replaces this device's sync identity

- **Area:** 01 persistence & sync
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
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
@@ -64,5 +64,6 @@
     state=nextState;
     if(nkDurablePersist(state,'account switch')===false)throw new Error('Account progress could not be saved on this device.');
     nkSyncMeta=nextMeta;
+    nextMeta.deviceId = (nkSyncMeta && nkSyncMeta.deviceId) || nextMeta.deviceId;
     if(!nkSaveSyncMeta())throw new Error('Account sync history could not be saved on this device.');
     applySubject(SUBJECT_BY_NAME[snapshot.activeSubject]?snapshot.activeSubject:'Biochemistry');
     localStorage.removeItem(NK_PRE_CLOUD_BACKUP);```

## Verification

- Sign in on device A, sign out, sign in with an account whose snapshot was created on device B; confirm `nkSyncMeta.deviceId` is unchanged and still matches device A.
- Run `python3 tools/test_cross_device_sync_v1.py`.

## Alternatives considered

Preserving device ID in `nkSwitchLocalAccount` before writing the snapshot would also work, but restore is the single choke point used by both switch and recovery, so fixing it there covers both paths.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified cross_device_sync.js:62-66: nkRestoreAccountSnapshot assigns nkSyncMeta = nextMeta wholesale, and nextMeta.deviceId comes from the snapshot. nkNormalizeSyncMeta (line 27) only generates a device id when it is absent, so the foreign id survives. nkEnvelope (line 192) stamps ownerDevice with it and nkChooseWinner breaks ties on it. The one-line fix preserves this device id while keeping the account-scoped metadata. Approved.
