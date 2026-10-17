#!/usr/bin/env node
// Prévisualisation interactive dans le navigateur (équivalent local d'un « studio »).
import { serve } from './lib/server.mjs';
const { port } = await serve(Number(process.env.PORT ?? 3000));
console.log(`Studio : http://localhost:${port}/src/compositions/index.html?studio=1`);
console.log('Paramètres : &format=9x16|1x1|16x9  &subs=0  &t=12 (temps de départ).  Ctrl+C pour arrêter.');
