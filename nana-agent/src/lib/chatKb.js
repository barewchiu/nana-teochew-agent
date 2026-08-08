/**
 * DEMO chat turns + 乡音回复包 (public/audio/replies/)
 */

export const REPLY_VOICE_PACK = {
  eat: {
    audio: '/audio/replies/eat.m4a',
    reply: '食饱咯，阿嫲您呢？慢慢食，唔好急。',
    replyZh: '吃饱了，奶奶您呢？慢慢吃，别着急。',
  },
  meds: {
    audio: '/audio/replies/meds.m4a',
    reply: '阿嫲，爱准时食药啰，记得多饮水。我陪您记着。',
    replyZh: '奶奶，要按时吃药，记得多喝水。我帮您记着。',
  },
  miss_family: {
    audio: '/audio/replies/miss_family.m4a',
    reply: '阿公在天顶看着您，唔好哭，我陪您讲。',
    replyZh: '爷爷在天上看着您，别哭，我陪您说。',
  },
  affection: {
    audio: '/audio/replies/thanks.m4a',
    reply: '阿嫲，我也想您啰，我在这里陪您，慢慢讲。',
    replyZh: '奶奶，我也想您，我在这里陪您，慢慢说。',
  },
  thanks: {
    audio: '/audio/replies/thanks.m4a',
    reply: '阿嫲，我在这里，随时听您讲话。',
    replyZh: '奶奶，我在这里，随时听您说话。',
  },
  weather: {
    audio: '/audio/replies/weather.m4a',
    reply: '今日天时看着还好，阿嫲出门爱加件衫，免着凉。',
    replyZh: '今天天气看着还好，奶奶出门要加件衣服，别着凉。',
  },
  opera: {
    audio: '/audio/replies/opera.m4a',
    reply: '好呀阿嫲，想听潮剧就按绿色钮，我帮您开戏。',
    replyZh: '好呀奶奶，想听潮剧就按绿色按钮，我帮您打开。',
  },
  health: {
    audio: '/audio/replies/health.m4a',
    reply: '阿嫲身体有无要紧？慢慢讲，我听着。要紧就喊家里后生。',
    replyZh: '奶奶身体有没有事？慢慢说，我听着。要紧就叫家里年轻人。',
  },
  grandson: {
    audio: '/audio/replies/grandson.m4a',
    reply: '孙仔惦记您啰。想听留言，就按蓝色钮「听孙子的信」。',
    replyZh: '孙子惦记您呢。想听留言，就按蓝色按钮「听孙子的信」。',
  },
};

export const CHAT_TURNS = [
  {
    recognized: '哩食饱未？',
    recognizedZh: '你吃饱了吗？',
    ...REPLY_VOICE_PACK.eat,
    intent: 'eat',
  },
  {
    recognized: '今日想阿公了',
    recognizedZh: '今天想爷爷了',
    ...REPLY_VOICE_PACK.miss_family,
    intent: 'miss_family',
  },
  {
    recognized: '阿嫲爱食药未？',
    recognizedZh: '奶奶吃药了吗？',
    ...REPLY_VOICE_PACK.meds,
    intent: 'meds',
  },
  {
    recognized: '想听潮剧',
    recognizedZh: '想听潮剧',
    ...REPLY_VOICE_PACK.opera,
    intent: 'opera',
  },
  {
    recognized: '今日天气怎样？',
    recognizedZh: '今天天气怎么样？',
    ...REPLY_VOICE_PACK.weather,
    intent: 'weather',
  },
  {
    recognized: '身体有点不舒服',
    recognizedZh: '身体有点不舒服',
    ...REPLY_VOICE_PACK.health,
    intent: 'health',
  },
  {
    recognized: '孙子有无返来？',
    recognizedZh: '孙子有没有回来？',
    ...REPLY_VOICE_PACK.grandson,
    intent: 'grandson',
  },
  {
    recognized: '谢谢你陪我',
    recognizedZh: '谢谢你陪我',
    ...REPLY_VOICE_PACK.thanks,
    intent: 'thanks',
  },
  {
    recognized: '我想你',
    recognizedZh: '我想你',
    ...REPLY_VOICE_PACK.affection,
    intent: 'affection',
  },
];

/** P4：场景快捷钮（不依赖 Whisper，演示必中乡音包） */
export const SCENE_BUTTONS = [
  {
    id: 'eat',
    label: '吃饭',
    recognized: '哩食饱未？',
    recognizedZh: '你吃饱了吗？',
    topic: '吃饭',
    ...REPLY_VOICE_PACK.eat,
    intent: 'eat',
  },
  {
    id: 'meds',
    label: '吃药',
    recognized: '阿嫲爱食药未？',
    recognizedZh: '奶奶吃药了吗？',
    topic: '吃药',
    ...REPLY_VOICE_PACK.meds,
    intent: 'meds',
  },
  {
    id: 'miss_family',
    label: '想阿公',
    recognized: '今日想阿公了',
    recognizedZh: '今天想爷爷了',
    topic: '想阿公',
    ...REPLY_VOICE_PACK.miss_family,
    intent: 'miss_family',
  },
  {
    id: 'weather',
    label: '天气',
    recognized: '今日天气怎样？',
    recognizedZh: '今天天气怎么样？',
    topic: '天气',
    ...REPLY_VOICE_PACK.weather,
    intent: 'weather',
  },
  {
    id: 'opera',
    label: '潮剧',
    recognized: '想听潮剧',
    recognizedZh: '想听潮剧',
    topic: '潮剧',
    ...REPLY_VOICE_PACK.opera,
    intent: 'opera',
  },
  {
    id: 'grandson',
    label: '孙子',
    recognized: '孙子有无返来？',
    recognizedZh: '孙子有没有回来？',
    topic: '孙子',
    ...REPLY_VOICE_PACK.grandson,
    intent: 'grandson',
  },
  {
    id: 'health',
    label: '身体',
    recognized: '身体有点不舒服',
    recognizedZh: '身体有点不舒服',
    topic: '身体',
    ...REPLY_VOICE_PACK.health,
    intent: 'health',
  },
  {
    id: 'affection',
    label: '想你',
    recognized: '我想你',
    recognizedZh: '我想你',
    topic: '想念陪伴',
    ...REPLY_VOICE_PACK.affection,
    intent: 'affection',
  },
];

/** 承接上一话题的续话钮（配合 P3） */
export const FOLLOWUP_BUTTONS = {
  meds: [
    {
      id: 'meds_done',
      label: '食了',
      recognized: '食了',
      recognizedZh: '吃了',
      reply: '好，阿嫲食药咯，真棒。记得多饮水，我陪您。',
      replyZh: '好，奶奶吃药了，真棒。记得多喝水，我陪着您。',
      audio: '/audio/replies/meds.m4a',
      intent: 'meds',
      topic: '吃药',
      followup: true,
    },
  ],
  weather: [
    {
      id: 'weather_hot',
      label: '好热',
      recognized: '好热',
      recognizedZh: '好热',
      reply: '热就少出门，在厝里吹风饮水，免中暑。',
      replyZh: '热就少出门，在家里吹风喝水，别中暑。',
      audio: '/audio/replies/weather.m4a',
      intent: 'weather',
      topic: '天气',
      followup: true,
    },
  ],
  eat: [
    {
      id: 'eat_done',
      label: '食饱了',
      recognized: '食饱了',
      recognizedZh: '吃饱了',
      reply: '好呀，食饱正有力气。阿嫲慢慢歇一下。',
      replyZh: '好呀，吃饱才有力气。奶奶慢慢歇一会儿。',
      audio: '/audio/replies/eat.m4a',
      intent: 'eat',
      topic: '吃饭',
      followup: true,
    },
  ],
};

export const INTENT_TOPIC_LABELS = {
  eat: '吃饭',
  meds: '吃药',
  miss_family: '想阿公',
  affection: '想念陪伴',
  thanks: '道谢',
  weather: '天气',
  opera: '潮剧',
  health: '身体',
  grandson: '孙子',
};

/** Map LIVE API audio / intent to voice-pack path */
export function resolveChatAudio({ audio, intent, reply } = {}) {
  if (audio) return audio;
  if (intent && REPLY_VOICE_PACK[intent]?.audio) {
    return REPLY_VOICE_PACK[intent].audio;
  }
  const text = `${reply || ''}`;
  if (/食饱|食糜|吃饭/.test(text)) return REPLY_VOICE_PACK.eat.audio;
  if (/食药|吃药/.test(text)) return REPLY_VOICE_PACK.meds.audio;
  if (/阿公|唔好哭/.test(text)) return REPLY_VOICE_PACK.miss_family.audio;
  if (/我也想您|陪您/.test(text)) return REPLY_VOICE_PACK.affection.audio;
  if (/孙子|留言/.test(text)) return REPLY_VOICE_PACK.grandson.audio;
  if (/天时|天气|着凉/.test(text)) return REPLY_VOICE_PACK.weather.audio;
  if (/潮剧|开戏/.test(text)) return REPLY_VOICE_PACK.opera.audio;
  if (/身体|后生/.test(text)) return REPLY_VOICE_PACK.health.audio;
  if (/我在这里|随时听/.test(text)) return REPLY_VOICE_PACK.thanks.audio;
  return null;
}
