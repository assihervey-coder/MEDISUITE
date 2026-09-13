/**
 * File d'attente IndexedDB du mode offline (v0.7).
 *
 * Les mutations (POST eCRF notamment) effectuées hors connexion sont
 * persistées localement puis rejouées au retour du réseau avec une
 * clé d'idempotence — le serveur eCRF dédoublonne par clé calculée
 * (medisuite_core/ecrf.py dedup_key), donc un rejeu ne crée JAMAIS
 * de doublon (sécurité clinique §8 du protocole CI-01).
 */

/** Opération en attente de synchronisation. */
export interface QueuedOp {
  id?: number;
  /** clé d'idempotence envoyée au serveur (header Idempotency-Key). */
  key: string;
  method: "POST" | "PUT" | "PATCH";
  path: string;
  body: unknown;
  createdAt: number;
  /** tentatives de rejeu (back-off exponentiel). */
  tries: number;
  lastError?: string;
}

const DB_NAME = "medisuite-offline";
const DB_VERSION = 1;
const STORE_PENDING = "pending";
const STORE_DEAD = "dead";

let dbPromise: Promise<IDBDatabase> | null = null;

/** Ouvre (ou crée) la base IndexedDB — testable via injection. */
export function openDb(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE_PENDING)) {
        db.createObjectStore(STORE_PENDING, { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains(STORE_DEAD)) {
        db.createObjectStore(STORE_DEAD, { keyPath: "id", autoIncrement: true });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error("IndexedDB indisponible"));
  });
  return dbPromise;
}

function tx(db: IDBDatabase, store: string, mode: IDBTransactionMode): IDBObjectStore {
  return db.transaction(store, mode).objectStore(store);
}

function asPromise<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error("IndexedDB erreur"));
  });
}

/** Empile une opération hors-ligne (FIFO). */
export async function enqueue(op: Omit<QueuedOp, "id" | "tries">): Promise<number> {
  const db = await openDb();
  const record: QueuedOp = { ...op, tries: 0 };
  const req = tx(db, STORE_PENDING, "readwrite").add(record);
  const id = await asPromise(req) as IDBValidKey as number;
  return id;
}

/** Toutes les opérations en attente, dans l'ordre d'empilement. */
export async function listPending(): Promise<QueuedOp[]> {
  const db = await openDb();
  const all = (await asPromise(
    tx(db, STORE_PENDING, "readonly").getAll() as IDBRequest<QueuedOp[]>
  )) as QueuedOp[];
  return all.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));
}

export async function removePending(id: number): Promise<void> {
  const db = await openDb();
  await asPromise(tx(db, STORE_PENDING, "readwrite").delete(id));
}

/** Rejet définitif (4xx hors 408/429) : mis de côté pour inspection UI. */
export async function moveToDead(op: QueuedOp): Promise<void> {
  const db = await openDb();
  const clone: QueuedOp = { ...op };
  delete clone.id;
  const store = tx(db, STORE_DEAD, "readwrite");
  await asPromise(store.add(clone));
  if (op.id !== undefined) await removePending(op.id);
}

export async function countDead(): Promise<number> {
  const db = await openDb();
  return asPromise(tx(db, STORE_DEAD, "readonly").count());
}

export async function clearDead(): Promise<void> {
  const db = await openDb();
  await asPromise(tx(db, STORE_DEAD, "readwrite").clear());
}
