import { enrichWithLexicon, pickNextLexiconLesson } from './teochewKb';

/** Fetch next mentor question — Teochew prefers local KB; else backend AI */
export async function fetchMentorQuestion({ dialect, learned }) {
  // Local knowledge base first for Teochew (stable + correct 本字/潮拼)
  if (dialect === 'teochew') {
    const kbLesson = pickNextLexiconLesson(learned);
    if (kbLesson) {
      return { ...kbLesson, brain: 'knowledge-base', source: 'kb' };
    }
  }

  const resp = await fetch('/api/mentor/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dialect, learned }),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = data.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      : detail || `出题失败 ${resp.status}`;
    throw new Error(msg);
  }

  const lesson = {
    wordZh: data.word_zh,
    prompt: data.prompt,
    promptZh: data.prompt_zh,
    noteHint: data.note_hint,
    source: data.source || 'ai',
    brain: data.brain,
    demoWord: data.teochew || data.word_zh,
    demoReply: data.teochew
      ? `${data.teochew}！（${data.pengim || ''}）老师，我讲得正宗吗？`
      : `学会了「${data.word_zh}」！老师，我讲得正宗吗？`,
    demoReplyZh: `学会了「${data.word_zh}」！老师，我读得标准吗？`,
    teochew: data.teochew || '',
    colloquial: data.colloquial || '',
    pengim: data.pengim || '',
    audioAsk: '/heritage_ask.m4a',
    audioLearned: '/heritage_learned.m4a',
  };

  return dialect === 'teochew' ? enrichWithLexicon(lesson) : lesson;
}

export function learnedWordsFromBook(entries, dialectId) {
  return entries
    .filter((e) => e.dialectId === dialectId)
    .map((e) => e.wordZh || e.word)
    .filter(Boolean);
}
