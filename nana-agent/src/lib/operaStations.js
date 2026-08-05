/**
 * Teochew opera / radio stations.
 * Operas expose multiple short clips picked from different parts of the full recording.
 */

export const operaStations = [
  {
    id: 'su_liu_niang',
    title: '苏六娘',
    subtitle: '经典潮剧 · 选段播放',
    color: 'from-emerald-500 to-teal-600',
    externalUrl:
      'https://search.bilibili.com/all?keyword=%E6%BD%AE%E5%89%A7%E8%8B%8F%E5%85%AD%E5%A8%98',
    preferExternal: false,
    clips: [
      { id: 's1', label: '第一段 · 开场', audio: '/audio/su_liu_niang_01.mp3' },
      { id: 's2', label: '第二段 · 选段', audio: '/audio/su_liu_niang_02.mp3' },
      { id: 's3', label: '第三段 · 选段', audio: '/audio/su_liu_niang_03.mp3' },
      { id: 's4', label: '第四段 · 选段', audio: '/audio/su_liu_niang_04.mp3' },
      { id: 's5', label: '第五段 · 选段', audio: '/audio/su_liu_niang_05.mp3' },
    ],
  },
  {
    id: 'gao_qin_fu',
    title: '告亲夫',
    subtitle: '传统名段 · 选段播放',
    color: 'from-green-600 to-emerald-700',
    externalUrl:
      'https://search.bilibili.com/all?keyword=%E6%BD%AE%E5%89%A7%E5%91%8A%E4%BA%B2%E5%A4%AB',
    preferExternal: false,
    clips: [
      { id: 'g1', label: '第一段 · 开场', audio: '/audio/gao_qin_fu_01.mp3' },
      { id: 'g2', label: '第二段 · 选段', audio: '/audio/gao_qin_fu_02.mp3' },
      { id: 'g3', label: '第三段 · 选段', audio: '/audio/gao_qin_fu_03.mp3' },
      { id: 'g4', label: '第四段 · 选段', audio: '/audio/gao_qin_fu_04.mp3' },
      { id: 'g5', label: '第五段 · 选段', audio: '/audio/gao_qin_fu_05.mp3' },
    ],
  },
  {
    id: 'teochew_radio',
    title: '潮语广播',
    subtitle: '汕头经济广播 · 在线收听',
    color: 'from-teal-500 to-cyan-600',
    audio: null,
    clips: null,
    externalUrl: 'https://tingfm.com/radio/146',
    preferExternal: true,
  },
];
