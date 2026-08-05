import { findVoiceClip } from './dialectBook';

/**
 * Resolve which audio to play for an AI reply:
 * 1) explicit teacher recording from this turn
 * 2) matching clip in digital genealogy
 * 3) pre-recorded demo file / null (caller may TTS)
 */
export function resolveReplyAudio({
  teacherAudio,
  fallbackAudio,
  bookEntries,
  matchKeys = [],
}) {
  if (teacherAudio) {
    return { src: teacherAudio, kind: 'teacher' };
  }
  const clip = findVoiceClip(bookEntries, matchKeys);
  if (clip?.audioDataUrl) {
    return { src: clip.audioDataUrl, kind: 'genealogy', entry: clip };
  }
  if (fallbackAudio) {
    return { src: fallbackAudio, kind: 'preset' };
  }
  return { src: null, kind: 'none' };
}
