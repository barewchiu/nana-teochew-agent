/** Post-teaching "service promise" — digital inclusion, not quiz score */

export function getServiceReward(lesson) {
  const wordZh = lesson?.wordZh || '';
  const teochew = lesson?.teochew || lesson?.demoWord || wordZh;
  const type = lesson?.type || lesson?.category || '';

  if (
    type.includes('反诈') ||
    /骗子|转账|汇款|假的|不要相信|报警/.test(wordZh)
  ) {
    return {
      title: '数字化服务已解锁',
      promise: `谢谢老师！我记住了「${teochew}」。以后您遇到可疑短信，可以用乡音告诉我，我来当您的数字保镖。`,
      promiseZh: `我已适配「${wordZh}」。您可用方言描述可疑信息，我会帮您留意风险。`,
      legacyNote: '这段乡音已作为数字遗产保存，可供后辈理解您的提醒。',
    };
  }

  if (/谢谢|多谢|不好意思|再见|你好/.test(wordZh)) {
    return {
      title: 'AI 适配进度 +1',
      promise: `谢谢老师教我「${teochew}」！学会了，我就能更自然地用乡音问候、道谢，陪您说话。`,
      promiseZh: `已学会「${wordZh}」。之后陪伴聊天时，我会优先听懂这句乡音。`,
      legacyNote: '寄语后辈：这是长辈亲授的礼貌用语，已写入数字族谱。',
    };
  }

  if (/爷爷|奶奶|爸爸|妈妈|外公|外婆|阿公|阿嫲|哥哥|姐姐/.test(wordZh)) {
    return {
      title: '家人称呼已记住',
      promise: `谢谢老师！我记住「${teochew}」是您家的称呼。以后您说起亲人，我就更能懂您心里想谁。`,
      promiseZh: `已适配亲属词「${wordZh}」。跨代沟通时，孙辈也能对照看到这句乡音。`,
      legacyNote: '寄语后辈：这是家里人的称呼，请好好听、好好记。',
    };
  }

  if (/吃|喝|睡觉|回去|房子|衣服|手机/.test(wordZh)) {
    return {
      title: '日常照料更懂您',
      promise: `谢谢老师！我学会了「${teochew}」。以后您用这句乡音说起吃饭、休息，我会更快明白您的需要。`,
      promiseZh: `已适配生活用语「${wordZh}」。目标是降低您使用数字服务的门槛。`,
      legacyNote: '数字遗产：日常生活的乡音，留给后辈听懂爷爷奶奶怎么说话。',
    };
  }

  return {
    title: 'AI 适配进度 +1',
    promise: `谢谢老师！我学会了「${teochew}」。这不是考试，是让我听得懂您——以后您可以直接用乡音使唤我。`,
    promiseZh: `已向您学习「${wordZh}」。所有适配都为了更好地照顾您，不是纠正您。`,
    legacyNote: '寄语后辈：这句乡音由长辈亲授，作为数字遗产保存。',
  };
}

export function humbleAskPrompt(wordZh, dialectLabel = '家乡话') {
  return {
    prompt: `老师，请教教我：${dialectLabel}里「${wordZh}」怎么说？学会了我就能更好地听懂您、照顾您。`,
    promptZh: `老师，请教我「${wordZh}」的乡音说法。我学会后，就能用您习惯的话来服务您。`,
  };
}
