import { useEffect, useRef, useState } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  MessageSquare,
  Music,
  ArrowLeft,
  Heart,
  Radio,
  Pill,
} from 'lucide-react';
import {
  grandsonMessages,
  medicationReminder,
} from './lib/voiceEchoMapping';
import { operaStations } from './lib/operaStations';
import { apiUrl } from './lib/api';

/** Modes: HOME | MSG | CHAT | OPERA */
const BAR_COUNT = 7;

const CHAT_TURNS = [
  {
    recognized: '哩食饱未？',
    recognizedZh: '你吃饱了吗？',
    reply: '食饱咯，阿嫲您呢？',
    replyZh: '吃饱了，奶奶您呢？',
    audio: '/audio/chat_1.m4a',
  },
  {
    recognized: '今日想阿公了',
    recognizedZh: '今天想爷爷了',
    reply: '阿公在天顶看着您，唔好哭，我陪您讲。',
    replyZh: '爷爷在天上看着您，别哭，我陪您说。',
    audio: '/audio/chat_2.m4a',
  },
  {
    recognized: '谢谢你陪我',
    recognizedZh: '谢谢你陪我',
    reply: '阿嫲，我在这里，随时听您讲话。',
    replyZh: '奶奶，我在这里，随时听您说话。',
    audio: '/audio/chat_3.m4a',
  },
];

function formatRecordTime(totalSeconds) {
  const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const ss = String(totalSeconds % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

function speakText(text, { rate = 0.85 } = {}) {
  if (!text || !window.speechSynthesis) return false;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'zh-CN';
  utter.rate = rate;
  window.speechSynthesis.speak(utter);
  return true;
}

function SoundWave({
  className = '',
  barClassName = 'bg-nana-warm',
  levels = null,
}) {
  const isLive = Array.isArray(levels);
  const bars = isLive
    ? levels
    : Array.from({ length: BAR_COUNT }, (_, i) => 0.35 + (i % 3) * 0.2);

  return (
    <div
      className={`flex h-16 items-end justify-center gap-1.5 ${className}`}
      aria-hidden="true"
    >
      {bars.map((level, i) => (
        <span
          key={i}
          className={`w-2.5 rounded-full sm:w-3 ${barClassName} ${
            isLive ? '' : 'sound-bar'
          }`}
          style={{
            height: `${10 + Math.min(1, Math.max(0.06, level)) * 54}px`,
            transition: isLive ? 'height 60ms linear' : undefined,
            animationDelay: isLive ? undefined : `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );
}

function App() {
  const [mode, setMode] = useState('HOME');
  const [status, setStatus] = useState('idle');
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [micError, setMicError] = useState('');
  const [pendingReply, setPendingReply] = useState(null);
  const [waveLevels, setWaveLevels] = useState(null);
  const [turnIndex, setTurnIndex] = useState(0);
  const [activeMsg, setActiveMsg] = useState(null);
  const [activeStation, setActiveStation] = useState(null);
  const [activeClip, setActiveClip] = useState(null);
  const [showReminder, setShowReminder] = useState(false);
  const [playHint, setPlayHint] = useState('');

  const audioRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const chunksRef = useRef([]);
  const recordTimerRef = useRef(null);
  const thinkTimerRef = useRef(null);
  const messagesEndRef = useRef(null);
  const turnIndexRef = useRef(0);
  const liveModeRef = useRef(false);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const rafRef = useRef(null);
  const processBlobRef = useRef(null);
  const reminderShownRef = useRef(false);

  useEffect(() => {
    turnIndexRef.current = turnIndex;
  }, [turnIndex]);

  useEffect(() => {
    liveModeRef.current = isLiveMode;
  }, [isLiveMode]);

  useEffect(() => {
    const audio = new Audio();
    audioRef.current = audio;
    const onEnded = () => {
      setIsPlaying(false);
      setPlayHint('');
    };
    const onPlay = () => setIsPlaying(true);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('pause', onEnded);
    audio.addEventListener('play', onPlay);
    return () => {
      audio.pause();
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('pause', onEnded);
      audio.removeEventListener('play', onPlay);
      audioRef.current = null;
      cleanupRecording();
      if (thinkTimerRef.current) clearTimeout(thinkTimerRef.current);
      window.speechSynthesis?.cancel();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, status]);

  // Soft medication reminder once when entering home
  useEffect(() => {
    if (reminderShownRef.current) return;
    reminderShownRef.current = true;
    const t = setTimeout(() => setShowReminder(true), 800);
    return () => clearTimeout(t);
  }, []);

  const stopAnalyser = () => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    analyserRef.current = null;
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setWaveLevels(null);
  };

  const startAnalyser = (stream) => {
    stopAnalyser();
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 128;
    analyser.smoothingTimeConstant = 0.7;
    source.connect(analyser);
    audioContextRef.current = ctx;
    analyserRef.current = analyser;
    const data = new Uint8Array(analyser.frequencyBinCount);
    const tick = () => {
      if (!analyserRef.current) return;
      analyserRef.current.getByteFrequencyData(data);
      const step = Math.max(1, Math.floor(data.length / BAR_COUNT));
      const next = [];
      for (let i = 0; i < BAR_COUNT; i += 1) {
        const idx = Math.min(data.length - 1, i * step + 2);
        next.push(data[idx] / 255);
      }
      setWaveLevels(next);
      rafRef.current = requestAnimationFrame(tick);
    };
    ctx.resume().catch(() => {});
    rafRef.current = requestAnimationFrame(tick);
  };

  const cleanupRecording = () => {
    if (recordTimerRef.current) {
      clearInterval(recordTimerRef.current);
      recordTimerRef.current = null;
    }
    stopAnalyser();
    if (mediaRecorderRef.current?.state === 'recording') {
      try {
        mediaRecorderRef.current.stop();
      } catch {
        /* ignore */
      }
    }
    mediaRecorderRef.current = null;
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
  };

  const stopAudio = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    window.speechSynthesis?.cancel();
    setIsPlaying(false);
  };

  const playAudioFile = (src, { fallbackText } = {}) => {
    const audio = audioRef.current;
    if (!audio || !src) {
      if (fallbackText) {
        const ok = speakText(fallbackText);
        setIsPlaying(ok);
        if (ok) {
          setTimeout(
            () => setIsPlaying(false),
            Math.max(2500, fallbackText.length * 280),
          );
        }
      }
      return;
    }
    stopAudio();
    audio.src = src;
    setIsPlaying(true);
    audio.play().catch(() => {
      setIsPlaying(false);
      if (fallbackText) {
        setPlayHint('乡音录音稍后补上，先用普通话念给您听');
        speakText(fallbackText);
        setIsPlaying(true);
        setTimeout(
          () => setIsPlaying(false),
          Math.max(2500, fallbackText.length * 280),
        );
      } else {
        setPlayHint('这段录音还没放进小管家里，请稍后再试');
      }
    });
  };

  const goHome = () => {
    stopAudio();
    cleanupRecording();
    if (thinkTimerRef.current) clearTimeout(thinkTimerRef.current);
    setMode('HOME');
    setStatus('idle');
    setMicError('');
    setPendingReply(null);
    setActiveMsg(null);
    setActiveStation(null);
    setActiveClip(null);
    setPlayHint('');
  };

  const openMessages = () => {
    stopAudio();
    setMode('MSG');
    setActiveMsg(null);
    setPlayHint('');
  };

  const playGrandsonMessage = (msg) => {
    setActiveMsg(msg);
    setPlayHint('');
    playAudioFile(msg.audio, {
      fallbackText: msg.teochewHint || msg.text,
    });
  };

  const playReminder = () => {
    playAudioFile(medicationReminder.audio, {
      fallbackText: medicationReminder.replyZh,
    });
  };

  const openChat = () => {
    stopAudio();
    cleanupRecording();
    setMode('CHAT');
    setStatus('idle');
    setMicError('');
    setPendingReply(null);
    setPlayHint('');
    if (messages.length === 0) {
      setMessages([
        {
          id: 'greet',
          role: 'ai',
          text: '阿嫲，食饱未？有事跟小管家讲就好。',
          translation: '奶奶，吃饱了吗？有事跟小管家说就好。',
        },
      ]);
    }
  };

  const openOpera = () => {
    stopAudio();
    setMode('OPERA');
    setActiveStation(null);
    setActiveClip(null);
    setPlayHint('');
  };

  const openStation = (station) => {
    setPlayHint('');
    if (station.preferExternal && station.externalUrl) {
      setActiveStation(station);
      setActiveClip(null);
      stopAudio();
      setIsPlaying(false);
      setPlayHint('正在打开电台收听页…');
      window.open(station.externalUrl, '_blank', 'noopener,noreferrer');
      return;
    }
    if (station.clips?.length) {
      stopAudio();
      setIsPlaying(false);
      setActiveStation(station);
      setActiveClip(null);
      return;
    }
    // Fallback: single audio
    setActiveStation(station);
    setActiveClip(null);
    if (station.audio) {
      playAudioFile(station.audio);
    } else if (station.externalUrl) {
      window.open(station.externalUrl, '_blank', 'noopener,noreferrer');
    }
  };

  const backToOperaList = () => {
    stopAudio();
    setActiveStation(null);
    setActiveClip(null);
    setPlayHint('');
  };

  const playClip = (clip) => {
    setActiveClip(clip);
    setPlayHint('');
    const audio = audioRef.current;
    if (!audio || !clip?.audio) return;
    stopAudio();
    audio.src = clip.audio;
    setIsPlaying(true);
    audio.play().catch(() => {
      setIsPlaying(false);
      setPlayHint('这段暂时播不了，请再试一次或打开外部链接。');
    });
  };

  const addMessage = (role, text, translation) => {
    setMessages((prev) => [
      ...prev,
      { id: `${Date.now()}-${Math.random()}`, role, text, translation },
    ]);
  };

  const applyReply = (replyPayload, { advanceDemoTurn = false } = {}) => {
    setPendingReply(replyPayload);
    addMessage('ai', replyPayload.reply, replyPayload.replyZh);
    setStatus('responding');
    if (advanceDemoTurn) {
      const next = (turnIndexRef.current + 1) % CHAT_TURNS.length;
      setTurnIndex(next);
    }
    if (replyPayload.audio) {
      playAudioFile(replyPayload.audio, {
        fallbackText: replyPayload.replyZh || replyPayload.reply,
      });
    } else {
      speakText(replyPayload.replyZh || replyPayload.reply);
      setIsPlaying(true);
      const approxMs = Math.max(
        2000,
        (replyPayload.replyZh || replyPayload.reply || '').length * 280,
      );
      setTimeout(() => setIsPlaying(false), approxMs);
    }
  };

  const runDemoFlow = () => {
    setStatus('thinking');
    if (thinkTimerRef.current) clearTimeout(thinkTimerRef.current);
    thinkTimerRef.current = setTimeout(() => {
      const turn = CHAT_TURNS[turnIndexRef.current];
      addMessage('user', turn.recognized, turn.recognizedZh);
      applyReply(
        {
          reply: turn.reply,
          replyZh: turn.replyZh,
          audio: turn.audio,
          recognized: turn.recognized,
          recognizedZh: turn.recognizedZh,
        },
        { advanceDemoTurn: true },
      );
    }, 1600);
  };

  const runLiveFlow = async (blob) => {
    setStatus('thinking');
    setMicError('');
    try {
      const form = new FormData();
      form.append('audio', blob, 'recording.webm');
      form.append('heritage', 'false');
      form.append('dialect', 'teochew');

      const resp = await fetch(apiUrl('/api/chat'), { method: 'POST', body: form });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        const detail = data.detail;
        const msg = Array.isArray(detail)
          ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
          : detail || `服务错误 ${resp.status}`;
        throw new Error(msg);
      }

      addMessage('user', data.transcript, data.transcript_zh);
      applyReply({
        reply: data.reply,
        replyZh: data.reply_zh,
        audio: null,
        recognized: data.transcript,
        recognizedZh: data.transcript_zh,
      });
    } catch (err) {
      console.error(err);
      setStatus('idle');
      setMicError(
        typeof err?.message === 'string'
          ? `阿嫲，小管家暂时听不清（${err.message}）。可先用演示模式。`
          : '阿嫲，小管家暂时听不清，请稍后再试。',
      );
    }
  };

  processBlobRef.current = async (blob) => {
    if (liveModeRef.current) runLiveFlow(blob);
    else runDemoFlow();
  };

  const startRecording = async () => {
    stopAudio();
    setMicError('');
    setPendingReply(null);

    if (!navigator.mediaDevices?.getUserMedia) {
      setMicError('请用 Chrome 打开，才能听您讲话');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      chunksRef.current = [];
      const mimeType = MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : undefined;
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || 'audio/webm',
        });
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((t) => t.stop());
          mediaStreamRef.current = null;
        }
        mediaRecorderRef.current = null;
        processBlobRef.current?.(blob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      startAnalyser(stream);
      setRecordSeconds(0);
      recordTimerRef.current = setInterval(() => {
        setRecordSeconds((s) => s + 1);
      }, 1000);
      setStatus('listening');
    } catch {
      setMicError('请允许用麦克风，小管家才能听您讲话');
      setStatus('idle');
    }
  };

  const stopRecordingAndRespond = () => {
    if (recordTimerRef.current) {
      clearInterval(recordTimerRef.current);
      recordTimerRef.current = null;
    }
    stopAnalyser();
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    } else {
      cleanupRecording();
      setMicError('没有录到声音，阿嫲再说一遍好吗？');
      setStatus('idle');
    }
  };

  const handleMicClick = () => {
    if (status === 'thinking') return;
    if (status === 'listening') stopRecordingAndRespond();
    else startRecording();
  };

  const statusHeadline = () => {
    if (micError) return micError;
    if (status === 'listening') {
      return `正在听您讲话… ${formatRecordTime(recordSeconds)}`;
    }
    if (status === 'thinking') {
      return isLiveMode ? '小管家正在听懂您…' : '小管家正在想怎么回您…';
    }
    if (status === 'responding' && pendingReply) {
      return `我听到了：${pendingReply.recognized}`;
    }
    return '按大红钮，跟小管家讲话';
  };

  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(ellipse_at_top,#fff7ed_0%,#ffedd5_45%,#fed7aa_100%)] px-5 py-6 sm:px-8">
      {/* Medication reminder toast */}
      {showReminder && mode === 'HOME' && (
        <div className="fixed inset-x-4 top-4 z-50 mx-auto max-w-lg rounded-3xl border-4 border-amber-500 bg-white p-5 shadow-2xl">
          <div className="flex items-start gap-3">
            <div className="rounded-2xl bg-amber-100 p-3">
              <Pill size={36} className="text-amber-700" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-bold text-amber-700">
                {medicationReminder.title}
              </p>
              <p className="mt-1 text-2xl font-black leading-snug text-nana-ink">
                {medicationReminder.reply}
              </p>
              <p className="mt-1 text-base text-gray-600">
                {medicationReminder.replyZh}
              </p>
              <div className="mt-4 flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    playReminder();
                  }}
                  className="flex-1 rounded-2xl bg-amber-600 py-3 text-lg font-bold text-white"
                >
                  听提醒
                </button>
                <button
                  type="button"
                  onClick={() => setShowReminder(false)}
                  className="flex-1 rounded-2xl border-2 border-gray-300 py-3 text-lg font-bold text-gray-600"
                >
                  知道了
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <header className="mb-6 text-center">
        <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-nana-warm/15">
          <Heart size={32} className="text-nana-warm" fill="currentColor" />
        </div>
        <h1 className="text-4xl font-black tracking-tight text-nana-ink sm:text-5xl">
          阿嫲的小管家
        </h1>
        <p className="mt-2 text-xl font-medium italic text-nana-warm sm:text-2xl">
          「阿嫲，食饱未？」
        </p>
        {mode !== 'HOME' && (
          <button
            type="button"
            onClick={goHome}
            className="mt-4 inline-flex items-center gap-2 rounded-full bg-white/90 px-5 py-2 text-lg font-bold text-nana-ink shadow"
          >
            <ArrowLeft size={22} />
            回首页
          </button>
        )}
      </header>

      {/* HOME — 3 giant buttons */}
      {mode === 'HOME' && (
        <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-5 pb-8">
          <button
            type="button"
            onClick={openMessages}
            className="flex h-44 flex-col items-center justify-center rounded-[2rem] bg-blue-500 text-white shadow-xl transition-transform active:scale-95 sm:h-48"
          >
            <MessageSquare size={64} strokeWidth={2.2} />
            <span className="mt-3 text-3xl font-black sm:text-4xl">
              听孙子的信
            </span>
            <span className="mt-1 text-base font-medium text-blue-100">
              普通话留言 · 用乡音念给您听
            </span>
          </button>

          <button
            type="button"
            onClick={openChat}
            className="flex h-44 flex-col items-center justify-center rounded-[2rem] bg-red-500 text-white shadow-xl transition-transform active:scale-95 sm:h-48"
          >
            <Mic size={64} strokeWidth={2.2} />
            <span className="mt-3 text-3xl font-black sm:text-4xl">
              跟管家讲话
            </span>
            <span className="mt-1 text-base font-medium text-red-100">
              用潮汕话跟我聊天
            </span>
          </button>

          <button
            type="button"
            onClick={openOpera}
            className="flex h-44 flex-col items-center justify-center rounded-[2rem] bg-emerald-500 text-white shadow-xl transition-transform active:scale-95 sm:h-48"
          >
            <Music size={64} strokeWidth={2.2} />
            <span className="mt-3 text-3xl font-black sm:text-4xl">
              听潮剧/广播
            </span>
            <span className="mt-1 text-base font-medium text-emerald-100">
              经典唱段 · 一键开听
            </span>
          </button>
        </main>
      )}

      {/* MSG — Grandson bridge */}
      {mode === 'MSG' && (
        <main className="mx-auto w-full max-w-lg flex-1">
          <p className="mb-4 text-center text-xl font-semibold text-nana-ink/80">
            孙子用普通话写的信，小管家用乡音念给您听
          </p>
          <div className="space-y-4">
            {grandsonMessages.map((msg) => (
              <button
                key={msg.id}
                type="button"
                onClick={() => playGrandsonMessage(msg)}
                className={`w-full rounded-3xl border-4 p-5 text-left transition-transform active:scale-[0.98] ${
                  activeMsg?.id === msg.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-blue-200 bg-white'
                }`}
              >
                <p className="text-sm font-bold text-blue-600">{msg.timeLabel}</p>
                <p className="mt-2 text-2xl font-bold leading-snug text-nana-ink">
                  {msg.text}
                </p>
                <p className="mt-2 text-lg text-gray-500">{msg.teochewHint}</p>
                <div className="mt-3 flex items-center gap-2 text-lg font-bold text-blue-600">
                  <Volume2 size={24} />
                  {activeMsg?.id === msg.id && isPlaying
                    ? '正在念给您听…'
                    : '点这里听乡音'}
                </div>
              </button>
            ))}
          </div>
          {playHint && (
            <p className="mt-4 text-center text-lg font-medium text-amber-700">
              {playHint}
            </p>
          )}
          {isPlaying && activeMsg && (
            <SoundWave className="mt-6" barClassName="bg-blue-500" />
          )}
        </main>
      )}

      {/* CHAT — Talk to helper */}
      {mode === 'CHAT' && (
        <main className="mx-auto flex w-full max-w-lg flex-1 flex-col">
          <div className="mb-4 flex items-center justify-between rounded-2xl border-2 border-orange-200 bg-white/90 px-4 py-3">
            <div className="flex items-center gap-2">
              <Radio
                size={26}
                className={isLiveMode ? 'text-green-600' : 'text-gray-400'}
              />
              <span className="text-base font-bold text-gray-800">
                {isLiveMode ? '真人听懂 LIVE' : '演示模式 DEMO'}
              </span>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={isLiveMode}
              onClick={() => {
                stopAudio();
                setIsLiveMode((v) => !v);
                setMicError('');
              }}
              className={`relative h-10 w-16 shrink-0 overflow-hidden rounded-full transition-colors ${
                isLiveMode ? 'bg-green-600' : 'bg-gray-400'
              }`}
            >
              <span
                className={`pointer-events-none absolute top-1 left-1 h-8 w-8 rounded-full bg-white shadow transition-transform duration-200 ${
                  isLiveMode ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {messages.length > 0 && (
            <div className="mb-4 max-h-44 space-y-3 overflow-y-auto rounded-2xl border-2 border-orange-200/80 bg-white/85 p-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`rounded-2xl px-4 py-3 ${
                    m.role === 'user'
                      ? 'ml-6 bg-red-500 text-white'
                      : 'mr-6 bg-orange-50 text-nana-ink'
                  }`}
                >
                  <p className="text-sm font-semibold opacity-80">
                    {m.role === 'user' ? '阿嫲' : '小管家'}
                  </p>
                  <p className="text-xl font-bold leading-snug sm:text-2xl">
                    {m.text}
                  </p>
                  {m.translation && (
                    <p
                      className={`mt-1 text-base ${
                        m.role === 'user' ? 'text-red-100' : 'text-gray-500'
                      }`}
                    >
                      {m.translation}
                    </p>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          <div className="flex flex-1 flex-col items-center justify-center py-4">
            <button
              type="button"
              onClick={handleMicClick}
              disabled={status === 'thinking'}
              aria-label={status === 'listening' ? '停止录音' : '开始说话'}
              className={`relative flex h-52 w-52 items-center justify-center rounded-full shadow-2xl transition-all active:scale-95 disabled:cursor-wait sm:h-60 sm:w-60 ${
                status === 'listening'
                  ? 'animate-pulse bg-red-600'
                  : status === 'thinking'
                    ? 'bg-red-400'
                    : 'bg-red-500 hover:bg-red-600'
              }`}
            >
              {status === 'listening' ? (
                <>
                  <span className="absolute inset-0 rounded-full bg-red-400/40 animate-ping" />
                  <MicOff size={96} color="white" strokeWidth={2.4} />
                </>
              ) : (
                <Mic size={96} color="white" strokeWidth={2.4} />
              )}
            </button>

            {status === 'listening' && (
              <SoundWave className="mt-6" levels={waveLevels} barClassName="bg-red-500" />
            )}

            <p
              className={`mt-6 min-h-[3.5rem] max-w-xl text-center text-2xl font-bold sm:text-3xl ${
                micError ? 'text-red-700' : 'text-nana-ink'
              }`}
            >
              {statusHeadline()}
            </p>
          </div>

          {status === 'responding' && pendingReply && (
            <div className="mb-4 rounded-3xl border-4 border-nana-warm bg-white p-6 shadow-md">
              <p className="text-3xl font-bold leading-snug text-nana-ink sm:text-4xl">
                {pendingReply.reply}
              </p>
              <p className="mt-2 text-xl text-gray-600">{pendingReply.replyZh}</p>
              {isPlaying && (
                <SoundWave className="my-4" barClassName="bg-nana-warm" />
              )}
              <button
                type="button"
                onClick={() =>
                  playAudioFile(pendingReply.audio, {
                    fallbackText: pendingReply.replyZh || pendingReply.reply,
                  })
                }
                className="mt-3 flex w-full items-center justify-center gap-3 rounded-2xl bg-red-500 px-6 py-4 text-2xl font-bold text-white"
              >
                <Volume2 size={36} />
                {isPlaying ? '正在讲…' : '再听一遍'}
              </button>
            </div>
          )}
        </main>
      )}

      {/* OPERA */}
      {mode === 'OPERA' && (
        <main className="mx-auto w-full max-w-lg flex-1">
          {activeStation?.clips?.length ? (
            <>
              <button
                type="button"
                onClick={backToOperaList}
                className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/90 px-5 py-2 text-lg font-bold text-nana-ink shadow"
              >
                <ArrowLeft size={22} />
                回剧目列表
              </button>
              <p className="mb-2 text-center text-3xl font-black text-nana-ink">
                {activeStation.title}
              </p>
              <p className="mb-4 text-center text-lg text-nana-ink/70">
                选一段听，每段都是戏里不同地方的选段
              </p>
              <div className="space-y-3">
                {activeStation.clips.map((clip, idx) => (
                  <button
                    key={clip.id}
                    type="button"
                    onClick={() => playClip(clip)}
                    className={`flex w-full items-center gap-4 rounded-3xl border-4 px-5 py-5 text-left transition-transform active:scale-[0.98] ${
                      activeClip?.id === clip.id
                        ? 'border-emerald-600 bg-emerald-50'
                        : 'border-emerald-200 bg-white'
                    }`}
                  >
                    <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-500 text-2xl font-black text-white">
                      {idx + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-2xl font-black text-nana-ink">{clip.label}</p>
                      <p className="mt-1 text-base font-bold text-emerald-700">
                        {activeClip?.id === clip.id && isPlaying
                          ? '正在播放…'
                          : '点这里听'}
                      </p>
                    </div>
                    <Volume2 size={28} className="text-emerald-600" />
                  </button>
                ))}
              </div>
              {activeStation.externalUrl && (
                <a
                  href={activeStation.externalUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 block rounded-2xl bg-emerald-700 py-3 text-center text-lg font-bold text-white underline"
                >
                  打开外部完整潮剧
                </a>
              )}
            </>
          ) : (
            <>
              <p className="mb-4 text-center text-xl font-semibold text-nana-ink/80">
                点一张卡片，小管家帮您开戏
              </p>
              <div className="space-y-4">
                {operaStations.map((station) => (
                  <div
                    key={station.id}
                    className={`overflow-hidden rounded-3xl bg-gradient-to-br ${station.color} p-1 shadow-xl`}
                  >
                    <button
                      type="button"
                      onClick={() => openStation(station)}
                      className="flex w-full items-center gap-4 rounded-[1.35rem] bg-white/10 px-5 py-6 text-left text-white backdrop-blur-sm transition-transform active:scale-[0.98]"
                    >
                      <div className="rounded-2xl bg-white/20 p-4">
                        <Music size={40} />
                      </div>
                      <div className="flex-1">
                        <p className="text-3xl font-black">{station.title}</p>
                        <p className="mt-1 text-lg text-white/90">{station.subtitle}</p>
                        <p className="mt-2 text-base font-bold">
                          {station.preferExternal
                            ? '点这里打开电台'
                            : station.clips?.length
                              ? `共 ${station.clips.length} 段可选`
                              : '点这里听'}
                        </p>
                      </div>
                    </button>
                    {station.preferExternal && station.externalUrl && (
                      <a
                        href={station.externalUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="block bg-black/20 px-5 py-3 text-center text-lg font-bold text-white underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        打开在线电台
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
          {playHint && (
            <p className="mt-4 text-center text-lg font-medium text-amber-800">
              {playHint}
            </p>
          )}
          {isPlaying && activeClip && (
            <SoundWave className="mt-6" barClassName="bg-emerald-600" />
          )}
        </main>
      )}
    </div>
  );
}

export default App;
