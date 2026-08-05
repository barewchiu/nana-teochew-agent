import { buildTeochewMentorLessons } from './teochewKb';

/** Multi-dialect config + DEMO mentor curriculum */

export const DIALECTS = [
  {
    id: 'teochew',
    label: '潮汕话',
    labelEn: 'Teochew',
    region: '中国潮汕 · 东南亚潮籍',
    chatHint: '按蓝色按钮，用乡音跟我说——我来听懂您',
    noteHint: '这段乡音已作为数字遗产保存',
    /** Built from 潮汕话常用词汇表 knowledge base */
    mentorLessons: buildTeochewMentorLessons(),
  },
  {
    id: 'hokkien',
    label: '福建话',
    labelEn: 'Hokkien',
    region: '新加坡 · 马来西亚 · 闽南',
    chatHint: '按蓝色按钮，用乡音跟我说——我来听懂您',
    noteHint: '这段乡音已作为数字遗产保存',
    mentorLessons: [
      {
        wordZh: '谢谢',
        prompt: '老师老师，福建话里的「谢谢」怎么说呀？',
        promptZh: '老师，请问家乡话怎么说「谢谢」？',
        demoWord: '多谢',
        demoReply: '多谢！老师，我讲得对吗？',
        demoReplyZh: '多谢！老师，我读得对吗？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
      {
        wordZh: '对不起',
        prompt: '老师，「对不起」福建话怎么讲？',
        promptZh: '老师，家乡话怎么说「对不起」？',
        demoWord: '对不住',
        demoReply: '对不住！老师，这样可以吗？',
        demoReplyZh: '对不起！老师，这样可以吗？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
      {
        wordZh: '吃饭',
        prompt: '老师，「吃饭」福建话怎么说？',
        promptZh: '老师，家乡话怎么说「吃饭」？',
        demoWord: '食饭',
        demoReply: '食饭！老师，我有学着吗？',
        demoReplyZh: '吃饭！老师，我学得怎么样？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
    ],
  },
  {
    id: 'cantonese',
    label: '粤语',
    labelEn: 'Cantonese',
    region: '粤港澳 · 海外粤籍',
    chatHint: '按蓝色按钮，用乡音跟我说——我来听懂您',
    noteHint: '这段乡音已作为数字遗产保存',
    mentorLessons: [
      {
        wordZh: '谢谢',
        prompt: '老师老师，粤语里的「谢谢」怎么说呀？',
        promptZh: '老师，请问家乡话怎么说「谢谢」？',
        demoWord: '唔该',
        demoReply: '唔该！老师，我讲得似吗？',
        demoReplyZh: '谢谢！老师，我读得像吗？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
      {
        wordZh: '对不起',
        prompt: '老师，「对不起」粤语怎么讲？',
        promptZh: '老师，家乡话怎么说「对不起」？',
        demoWord: '对唔住',
        demoReply: '对唔住！老师，得唔得？',
        demoReplyZh: '对不起！老师，可以吗？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
      {
        wordZh: '吃饭',
        prompt: '老师，「吃饭」粤语怎么说？',
        promptZh: '老师，家乡话怎么说「吃饭」？',
        demoWord: '食饭',
        demoReply: '食饭！老师，我学会了吗？',
        demoReplyZh: '吃饭！老师，我学会了吗？',
        audioAsk: '/heritage_ask.m4a',
        audioLearned: '/heritage_learned.m4a',
        source: 'demo',
      },
    ],
  },
];

export function getDialect(id) {
  return DIALECTS.find((d) => d.id === id) || DIALECTS[0];
}

export function getDemoLesson(dialectId, index) {
  const d = getDialect(dialectId);
  const lessons = d.mentorLessons || [];
  if (!lessons.length) return null;
  return lessons[((index % lessons.length) + lessons.length) % lessons.length];
}
