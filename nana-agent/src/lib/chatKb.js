/**
 * DEMO chat turns + intent→audio helpers for Teochew companion chat.
 */

export const CHAT_TURNS = [
  {
    recognized: '哩食饱未？',
    recognizedZh: '你吃饱了吗？',
    reply: '食饱咯，阿嫲您呢？慢慢食，唔好急。',
    replyZh: '吃饱了，奶奶您呢？慢慢吃，别着急。',
    audio: '/audio/chat_1.m4a',
    intent: 'eat',
  },
  {
    recognized: '今日想阿公了',
    recognizedZh: '今天想爷爷了',
    reply: '阿公在天顶看着您，唔好哭，我陪您讲。',
    replyZh: '爷爷在天上看着您，别哭，我陪您说。',
    audio: '/audio/chat_2.m4a',
    intent: 'miss_family',
  },
  {
    recognized: '阿嫲爱食药未？',
    recognizedZh: '奶奶吃药了吗？',
    reply: '阿嫲，爱准时食药啰，记得多饮水。我陪您记着。',
    replyZh: '奶奶，要按时吃药，记得多喝水。我帮您记着。',
    audio: '/audio/remind_meds.m4a',
    intent: 'meds',
  },
  {
    recognized: '想听潮剧',
    recognizedZh: '想听潮剧',
    reply: '好呀阿嫲，想听潮剧就按绿色钮，我帮您开戏。',
    replyZh: '好呀奶奶，想听潮剧就按绿色按钮，我帮您打开。',
    audio: null,
    intent: 'opera',
  },
  {
    recognized: '孙子有无返来？',
    recognizedZh: '孙子有没有回来？',
    reply: '孙仔惦记您啰。想听留言，就按蓝色钮「听孙子的信」。',
    replyZh: '孙子惦记您呢。想听留言，就按蓝色按钮「听孙子的信」。',
    audio: '/audio/miss_you.m4a',
    intent: 'grandson',
  },
  {
    recognized: '谢谢你陪我',
    recognizedZh: '谢谢你陪我',
    reply: '阿嫲，我在这里，随时听您讲话。',
    replyZh: '奶奶，我在这里，随时听您说话。',
    audio: '/audio/chat_3.m4a',
    intent: 'thanks',
  },
];

/** Map LIVE API audio field / intent to a playable public path */
export function resolveChatAudio({ audio, intent, reply } = {}) {
  if (audio) return audio;
  const map = {
    eat: '/audio/chat_1.m4a',
    miss_family: '/audio/chat_2.m4a',
    thanks: '/audio/chat_3.m4a',
    meds: '/audio/remind_meds.m4a',
    grandson: '/audio/miss_you.m4a',
  };
  if (intent && map[intent]) return map[intent];
  const text = `${reply || ''}`;
  if (/食饱|食糜|吃饭/.test(text)) return map.eat;
  if (/食药|吃药/.test(text)) return map.meds;
  if (/阿公|唔好哭/.test(text)) return map.miss_family;
  if (/孙子|留言/.test(text)) return map.grandson;
  if (/我在这里|随时听/.test(text)) return map.thanks;
  return null;
}
