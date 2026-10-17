#!/usr/bin/env node
// Mode B (facultatif) : génère la voix avec l'API ElevenLabs et récupère l'alignement mot à mot.
// La clé reste côté serveur : variables d'environnement ELEVENLABS_API_KEY et ELEVENLABS_VOICE_ID (jamais dans le navigateur).
import fs from 'node:fs';
import { p, readJson, writeJson } from './lib/util.mjs';

const key = process.env.ELEVENLABS_API_KEY, voice = process.env.ELEVENLABS_VOICE_ID;
if (!key || !voice) { console.log('Mode B ignoré : définissez ELEVENLABS_API_KEY et ELEVENLABS_VOICE_ID (voir README).'); process.exit(0); }
const script = readJson(p('src/config/script.json'));
const text = script.units.map((u) => u.text).join('\n\n');
const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}/with-timestamps?output_format=mp3_44100_128`, {
  method: 'POST', headers: { 'xi-api-key': key, 'Content-Type': 'application/json' },
  body: JSON.stringify({ text, model_id: process.env.ELEVENLABS_MODEL ?? 'eleven_multilingual_v2', language_code: 'fr' }),
});
if (!res.ok) { console.error(`ElevenLabs : erreur ${res.status}`, (await res.text()).slice(0, 300)); process.exit(1); }
const j = await res.json();
fs.writeFileSync(p('assets/audio/voix-generee.mp3'), Buffer.from(j.audio_base64, 'base64'));
writeJson(p('output/elevenlabs-alignement.json'), { alignment: j.alignment, normalized_alignment: j.normalized_alignment });
const a = readJson(p('src/config/audio.json')); a.voice = 'assets/audio/voix-generee.mp3'; writeJson(p('src/config/audio.json'), a);
console.log('Voix générée : assets/audio/voix-generee.mp3. Lancez : node scripts/align.mjs --audio assets/audio/voix-generee.mp3 --elevenlabs output/elevenlabs-alignement.json');
