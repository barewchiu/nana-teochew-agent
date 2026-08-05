/**
 * Fixed Teochew opera / radio cards — no search needed for hackathon demo.
 * Prefer local /audio/*.m4a when available; otherwise open external links.
 */

export const operaStations = [
  {
    id: 'su_liu_niang',
    title: '苏六娘',
    subtitle: '经典潮剧唱段',
    color: 'from-emerald-500 to-teal-600',
    audio: '/audio/opera_su_liu_niang.m4a',
    /** Fallback when local file missing */
    externalUrl: 'https://www.bilibili.com/video/BV1xx411c7mD',
  },
  {
    id: 'gao_qin_fu',
    title: '告亲夫',
    subtitle: '传统名段',
    color: 'from-green-600 to-emerald-700',
    audio: '/audio/opera_gao_qin_fu.m4a',
    externalUrl: 'https://www.bilibili.com/video/BV1xx411c7mD',
  },
  {
    id: 'teochew_radio',
    title: '潮语广播',
    subtitle: '乡音电台 · 陪您听',
    color: 'from-teal-500 to-cyan-600',
    audio: '/audio/teochew_radio.m4a',
    externalUrl: null,
  },
];
