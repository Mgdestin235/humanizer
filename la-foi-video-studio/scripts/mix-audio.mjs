// Mixage : voix (si alignée) + musique avec réduction automatique sous la voix + effets sonores.
import fs from 'node:fs';
import { p, run, readJson } from './lib/util.mjs';

export function mixAudio({ duration, useVoice, out = p('output/mix.m4a') }) {
  const a = readJson(p('src/config/audio.json'));
  const music = p(a.music), sfx = p('output/tmp/sfx.wav'), voice = p(a.voice);
  const fade = a.fadeOut ?? 2;
  const inputs = ['-i', music, '-i', sfx];
  let filter;
  if (useVoice && fs.existsSync(voice)) {
    inputs.push('-i', voice);
    filter =
      `[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=${a.voiceVolume},apad=whole_dur=${duration},asplit=2[v1][v2];` +
      `[0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=${a.musicVolume}[m];` +
      `[m][v2]sidechaincompress=threshold=0.02:ratio=${a.duckRatio}:attack=25:release=450:makeup=1[md];` +
      `[1:a]volume=${a.sfxVolume}[s];` +
      `[md][v1][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:${duration},afade=t=in:d=0.4,afade=t=out:st=${Math.max(0, duration - fade)}:d=${fade},loudnorm=I=-16:TP=-1.5:LRA=11[o]`;
  } else {
    filter =
      `[0:a]volume=${Math.min(1, a.musicVolume * 1.8)}[m];[1:a]volume=${a.sfxVolume}[s];` +
      `[m][s]amix=inputs=2:normalize=0:duration=longest,atrim=0:${duration},afade=t=in:d=0.6,afade=t=out:st=${Math.max(0, duration - fade)}:d=${fade},loudnorm=I=-16:TP=-1.5:LRA=11[o]`;
  }
  run('ffmpeg', ['-y', '-v', 'error', ...inputs, '-filter_complex', filter, '-map', '[o]', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', out]);
  return out;
}
