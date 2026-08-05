/** Anti-fraud prototype — rule-based for stable Pitch demos */
export const SAMPLE_SCAMS = [
  {
    id: 'prize',
    label: '中奖链接',
    text: '【恭喜】您的手机号已抽中iPhone一台，请点击 https://bit.ly/xxx 填写身份证与银行卡领取。',
  },
  {
    id: 'police',
    label: '冒充公检法',
    text: '我是公安局的，你的银行账户涉嫌洗钱，请立即把钱转到安全账户配合调查，否则将被逮捕。',
  },
  {
    id: 'family',
    label: '假冒亲友',
    text: '妈，我手机掉了，用同学号联系你。我在外面出事了，先打5000块到这个卡里救急。',
  },
];

const RISK_KEYWORDS = [
  '中奖',
  '点击',
  '领取',
  '身份证',
  '银行卡',
  '转账',
  '安全账户',
  '公安',
  '检察院',
  '法院',
  '洗钱',
  '逮捕',
  '验证码',
  '退税',
  '退款',
  'http',
  'bit.ly',
];

export function analyzeScamText(text) {
  const content = (text || '').trim();
  if (!content) {
    return {
      risk: 'none',
      score: 0,
      title: '请先粘贴可疑短信',
      reply: '把短信贴上来，我帮您看一看。',
      replyZh: '请粘贴短信内容后再扫描。',
      reasons: [],
    };
  }

  const hits = RISK_KEYWORDS.filter((k) =>
    content.toLowerCase().includes(k.toLowerCase()),
  );
  const score = Math.min(100, hits.length * 18 + (content.includes('http') ? 20 : 0));

  if (score >= 36) {
    return {
      risk: 'high',
      score,
      title: '高风险！疑似诈骗',
      reply: '阿公阿嫲，这是骗人的！千万勿转账、勿点链接！',
      replyZh: '外公外婆，这是诈骗！千万不要转账，不要点链接！',
      reasons: hits.slice(0, 5),
    };
  }

  if (score >= 18) {
    return {
      risk: 'medium',
      score,
      title: '有可疑迹象',
      reply: '这条信息怪怪的，先问家里后生再处理。',
      replyZh: '这条信息有点可疑，先问家人再处理。',
      reasons: hits.slice(0, 5),
    };
  }

  return {
    risk: 'low',
    score,
    title: '暂未发现明显诈骗话术',
    reply: '看着还好，但陌生链接都勿乱点。',
    replyZh: '暂时看不出明显诈骗，但陌生链接都不要点。',
    reasons: hits,
  };
}

export const ANTI_FRAUD_AUDIO = '/anti_fraud_teochew.m4a';
