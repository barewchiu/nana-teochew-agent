import lexicon from '../data/teochew_lexicon.json';
import dialogues from '../data/teochew_dialogues.json';

/** Preferred DEMO curriculum order (普通话 keys in lexicon) */
const MENTOR_CURRICULUM = [
  '谢谢',
  '不好意思',
  '你好！',
  '你好',
  '再见',
  '吃饭了吗？',
  '爷爷',
  '奶奶',
  '吃',
  '回去',
  '知道',
  '什么',
  '骗子',
  '转账、汇款',
  '不要相信',
];

function norm(s) {
  return String(s || '')
    .replace(/[！!？?]/g, '')
    .trim();
}

export function getLexicon() {
  return lexicon;
}

export function getDialogues() {
  return dialogues;
}

export function lookupByMandarin(mandarin) {
  const key = norm(mandarin);
  return (
    lexicon.find((e) => norm(e.mandarin) === key) ||
    lexicon.find(
      (e) =>
        norm(e.mandarin).includes(key) || key.includes(norm(e.mandarin)),
    ) ||
    null
  );
}

export function entryToLesson(entry, { source = 'kb' } = {}) {
  if (!entry) return null;
  const wordZh = norm(entry.mandarin) || entry.mandarin;
  return {
    wordZh,
    prompt: `老师，请教教我：潮汕话里「${wordZh}」怎么说？学会了我就能更好地听懂您、照顾您。`,
    promptZh: `老师，请教我「${wordZh}」的乡音。我不是来考您，是来向您学习，好让数字世界听得懂您。`,
    demoWord: entry.teochew,
    demoReply: `谢谢老师！我记住了「${entry.teochew}」。`,
    demoReplyZh: `谢谢老师！「${wordZh}」我说成「${entry.teochew}」（${entry.pengim}）。以后我会用这句话更好地服务您。`,
    teochew: entry.teochew,
    colloquial: entry.colloquial,
    pengim: entry.pengim,
    category: entry.category,
    type: entry.type,
    lexiconId: entry.id,
    noteHint: `数字遗产：${wordZh} → ${entry.teochew}｜潮拼 ${entry.pengim}。由长辈亲授，不是批改作业。`,
    audioAsk: '/heritage_ask.m4a',
    audioLearned: '/heritage_learned.m4a',
    source,
  };
}

/** DEMO fixed curriculum built from lexicon */
export function buildTeochewMentorLessons() {
  const lessons = [];
  const seen = new Set();
  for (const key of MENTOR_CURRICULUM) {
    const entry = lookupByMandarin(key);
    if (!entry || seen.has(entry.id)) continue;
    seen.add(entry.id);
    lessons.push(entryToLesson(entry, { source: 'kb' }));
  }
  // Fill with more short phrases / words if curriculum short
  for (const entry of lexicon) {
    if (lessons.length >= 12) break;
    if (seen.has(entry.id)) continue;
    if (entry.type === 'anti_fraud' || entry.type === 'phrase' || entry.type === 'word') {
      seen.add(entry.id);
      lessons.push(entryToLesson(entry, { source: 'kb' }));
    }
  }
  return lessons;
}

/** Pick next unused lexicon entry for continuous mentor learning */
export function pickNextLexiconLesson(learnedMandarin = []) {
  const learned = new Set(learnedMandarin.map(norm));
  const pool = [
    ...MENTOR_CURRICULUM.map(lookupByMandarin).filter(Boolean),
    ...lexicon.filter((e) => e.type === 'phrase' || e.type === 'word'),
    ...lexicon.filter((e) => e.type === 'anti_fraud'),
  ];
  const seen = new Set();
  for (const entry of pool) {
    if (!entry || seen.has(entry.id)) continue;
    seen.add(entry.id);
    if (!learned.has(norm(entry.mandarin))) {
      return entryToLesson(entry, { source: 'kb' });
    }
  }
  // All learned — wrap from start
  return entryToLesson(lexicon[0], { source: 'kb' });
}

export function enrichWithLexicon(lesson) {
  if (!lesson) return lesson;
  const entry = lookupByMandarin(lesson.wordZh);
  if (!entry) return lesson;
  return {
    ...lesson,
    teochew: lesson.teochew || entry.teochew,
    colloquial: lesson.colloquial || entry.colloquial,
    pengim: lesson.pengim || entry.pengim,
    demoWord: lesson.demoWord || entry.teochew,
    noteHint:
      lesson.noteHint ||
      `知识库对照：${norm(entry.mandarin)} → ${entry.teochew}｜潮拼 ${entry.pengim}`,
    lexiconId: entry.id,
  };
}

export function findDialogueByMandarin(text) {
  const key = norm(text);
  return (
    dialogues.find((d) => norm(d.mandarin) === key) ||
    dialogues.find((d) => norm(d.mandarin).includes(key)) ||
    null
  );
}
