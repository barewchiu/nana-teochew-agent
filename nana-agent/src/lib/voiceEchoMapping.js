/**
 * Mandarin → Teochew Voice Echo bridge
 * Hackathon approach: map grandson's Mandarin texts to pre-recorded Teochew audio.
 * Replace audio paths with real recordings when ready.
 */

export const grandsonMessages = [
  {
    id: 'back_home',
    text: '奶奶，我这周末回家看你，想吃你做的卤鹅。',
    teochewHint: '阿嫲，我这礼拜尾返去睇您，想食您煮个卤鹅。',
    audio: '/audio/back_home.m4a',
    timeLabel: '今天 10:00',
  },
  {
    id: 'remind_meds',
    text: '按时吃药，多喝水，别太累。',
    teochewHint: '爱准时食药，多饮水，勿伤过力。',
    audio: '/audio/remind_meds.m4a',
    timeLabel: '昨天',
  },
  {
    id: 'miss_you',
    text: '奶奶，我想你了。晚上早点休息。',
    teochewHint: '阿嫲，我想您啰。暝昏爱早歇。',
    audio: '/audio/miss_you.m4a',
    timeLabel: '前天',
  },
];

/** Startup medication reminder (spoken to Nana in Teochew style) */
export const medicationReminder = {
  id: 'meds_morning',
  title: '吃药提醒',
  reply: '阿嫲，爱食药啰，记得多饮水。',
  replyZh: '奶奶，该吃药了，记得多喝水。',
  audio: '/audio/remind_meds.m4a',
};

export function getGrandsonMessage(id) {
  return grandsonMessages.find((m) => m.id === id) || grandsonMessages[0];
}
