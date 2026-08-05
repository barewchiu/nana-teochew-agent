/**
 * Fixed Teochew opera / radio cards — no search needed for hackathon demo.
 * Local audio when present; otherwise open external listen pages.
 */

export const operaStations = [
  {
    id: 'su_liu_niang',
    title: '苏六娘',
    subtitle: '经典潮剧唱段',
    color: 'from-emerald-500 to-teal-600',
    audio: '/audio/opera_su_liu_niang.mp3',
    externalUrl: 'https://search.bilibili.com/all?keyword=%E6%BD%AE%E5%89%A7%E8%8B%8F%E5%85%AD%E5%A8%98',
    preferExternal: false,
  },
  {
    id: 'gao_qin_fu',
    title: '告亲夫',
    subtitle: '传统名段',
    color: 'from-green-600 to-emerald-700',
    audio: '/audio/opera_gao_qin_fu.mp3',
    externalUrl: 'https://search.bilibili.com/all?keyword=%E6%BD%AE%E5%89%A7%E5%91%8A%E4%BA%B2%E5%A4%AB',
    preferExternal: false,
  },
  {
    id: 'teochew_radio',
    title: '潮语广播',
    subtitle: '汕头经济广播 · 在线收听',
    color: 'from-teal-500 to-cyan-600',
    /** No local file — open live radio page */
    audio: null,
    externalUrl: 'https://tingfm.com/radio/146',
    preferExternal: true,
  },
];
