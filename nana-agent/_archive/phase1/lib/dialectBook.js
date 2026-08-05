const STORAGE_KEY = 'echo_of_roots_dialect_book_v2';
const MAX_ENTRIES = 30;
/** Keep audio on newest clips only — localStorage quota */
const MAX_WITH_AUDIO = 16;

function norm(s) {
  return String(s || '')
    .replace(/[！!？?。，、\s]/g, '')
    .trim()
    .toLowerCase();
}

export function loadDialectBook() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      // migrate v1 text-only book if present
      const legacy = localStorage.getItem('echo_of_roots_dialect_book_v1');
      if (!legacy) return [];
      const parsed = JSON.parse(legacy);
      return Array.isArray(parsed) ? parsed : [];
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveDialectBook(entries) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('录音转存失败'));
    reader.readAsDataURL(blob);
  });
}

function trimAudioQuota(entries) {
  let audioCount = 0;
  return entries.map((e) => {
    if (!e.audioDataUrl) return e;
    audioCount += 1;
    if (audioCount > MAX_WITH_AUDIO) {
      const { audioDataUrl, ...rest } = e;
      return { ...rest, audioPurged: true };
    }
    return e;
  });
}

export function addDialectEntry(entry) {
  const prev = loadDialectBook();
  const next = trimAudioQuota([
    {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      createdAt: new Date().toISOString(),
      hasAudio: Boolean(entry.audioDataUrl),
      ...entry,
    },
    ...prev,
  ]).slice(0, MAX_ENTRIES);

  try {
    saveDialectBook(next);
  } catch {
    // Quota exceeded — drop audio from oldest half and retry
    const slim = next.map((e, i) =>
      i > 5 && e.audioDataUrl
        ? (({ audioDataUrl, ...rest }) => ({ ...rest, hasAudio: false, audioPurged: true }))(e)
        : e,
    );
    saveDialectBook(slim);
    return slim;
  }
  return next;
}

export function clearDialectBook() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem('echo_of_roots_dialect_book_v1');
  return [];
}

export function formatEntryTime(iso) {
  try {
    return new Date(iso).toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '';
  }
}

/**
 * Find a stored teacher recording that matches any of the query keys
 * (普通话 / 潮语本字 / reply text snippets).
 */
export function findVoiceClip(entries, keys = []) {
  const list = Array.isArray(entries) ? entries : [];
  const queries = keys.map(norm).filter((k) => k.length >= 1);

  for (const e of list) {
    if (!e?.audioDataUrl) continue;
    const hay = [e.wordZh, e.word, e.teochew, e.colloquial]
      .map(norm)
      .filter(Boolean);
    const hit = queries.some((q) =>
      hay.some((h) => h === q || h.includes(q) || q.includes(h)),
    );
    if (hit) return e;
  }
  return null;
}

/** Pick first clip with audio (for demo showcase) */
export function latestVoiceClip(entries) {
  return (entries || []).find((e) => e.audioDataUrl) || null;
}
