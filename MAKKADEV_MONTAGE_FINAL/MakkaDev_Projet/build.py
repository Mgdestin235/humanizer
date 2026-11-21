#!/usr/bin/env python3
"""Montage MakkaDev : lit config.json et produit la vidéo, les sous-titres et la timeline.

Étapes :
  1. Chaque plan est découpé, stabilisé, ralenti si besoin, mis en 1080x1920 à 30 i/s.
  2. Les plans sont assemblés avec des fondus enchaînés discrets.
  3. Les textes animés et les sous-titres sont incrustés (fichier ASS).
  4. La voix off est placée sur la timeline, la musique baisse quand la voix parle.
  5. Export H.264 + AAC, SRT et timeline JSON.

Usage :  python3 build.py [--out DOSSIER_SORTIE] [--work DOSSIER_TRAVAIL] [--music FICHIER]
Pour ajuster le montage, modifiez config.json puis relancez. Les plans déjà calculés sont réutilisés.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--config", default=str(HERE / "config.json"))
ap.add_argument("--out", default=str(HERE.parent))
ap.add_argument("--work", default=str(HERE / "work"))
ap.add_argument("--music", default=None, help="fichier de musique à utiliser à la place de celui de config.json")
ap.add_argument("--no-voice", action="store_true", help="exporter sans voix off (sous-titres seulement)")
args = ap.parse_args()

CFG = json.loads(Path(args.config).read_text(encoding="utf-8"))
OUT = Path(args.out)
WORK = Path(args.work)
WORK.mkdir(parents=True, exist_ok=True)
FPS = CFG["fps"]
W, H = CFG["size"]
OV = CFG["transition_duration"]
TOTAL = CFG["total_duration"]
VOFF = CFG["voice"]["offset"]
ACCENT = "&H34B1F2&"  # ambre (BGR)


def run(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit("ERREUR ffmpeg :\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-2500:])
    return r


# ---------------------------------------------------------------- 1. plans
def plan_shots():
    shots = CFG["shots"]
    t = 0.0
    out = []
    for i, s in enumerate(shots):
        speed = s.get("speed", 1.0)
        head = 0.0 if i == 0 else OV / 2
        tail = 0.0 if i == len(shots) - 1 else OV / 2
        hold = s.get("hold_end", 0.0)
        length = head + s["dur"] + tail + hold
        src_start = max(0.0, s["ss"] - head * speed)
        src_len = (length - hold) * speed
        sp = dict(s, index=i, speed=speed, start=round(t, 3), end=round(t + s["dur"] + hold, 3),
                  head=head, tail=tail, hold=hold, length=length, src_start=src_start, src_len=src_len,
                  frames=round(length * FPS))
        out.append(sp)
        t += s["dur"]
    return out


def render_clip(sp):
    src = HERE / CFG["sources"][sp["src"]]
    key = hashlib.md5(json.dumps([sp["src"], sp["src_start"], sp["src_len"], sp["speed"], sp.get("interp"),
                                  sp["frames"], sp["hold"], W, H], sort_keys=True).encode()).hexdigest()[:8]
    out = WORK / f"clip_{sp['index']:02d}_{key}.mp4"
    if out.exists():
        return out
    trf = WORK / f"clip_{sp['index']:02d}.trf"
    inp = ["-ss", f"{sp['src_start']:.3f}", "-t", f"{sp['src_len'] + 0.3:.3f}", "-i", src]
    # passe 1 : analyse des mouvements de caméra
    run(["ffmpeg", "-v", "error", "-y", *inp, "-vf",
         f"fps={FPS},vidstabdetect=shakiness=5:accuracy=15:result={trf}", "-f", "null", "-"])
    chain = [f"fps={FPS}",
             f"vidstabtransform=input={trf}:smoothing=12:zoom=4:optzoom=0:interpol=bicubic",
             f"setpts=PTS/{sp['speed']}"]
    if sp.get("interp"):
        chain.append(f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    else:
        chain.append(f"fps={FPS}")
    chain += [f"scale={W}:{H}:flags=lanczos",
              "eq=contrast=1.04:saturation=1.06:brightness=0.005",
              "unsharp=5:5:0.5:5:5:0.0"]
    if sp["hold"]:
        chain.append(f"tpad=stop_mode=clone:stop_duration={sp['hold']}")
    chain += ["format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", *inp, "-vf", ",".join(chain), "-an", "-frames:v", sp["frames"],
         "-r", FPS, "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out])
    return out


# ---------------------------------------------------------------- 2. textes
def cues():
    """Sous-titres en temps vidéo, sans chevauchement."""
    raw = CFG["subtitles_voice_time"]
    out = []
    for i, (text, a, b) in enumerate(raw):
        end = b + 0.08
        if i + 1 < len(raw):
            end = min(end, raw[i + 1][1] - 0.02)
        out.append((text, a + VOFF, end + VOFF))
    return out


def ts(t):
    t = max(0.0, t)
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def circle(r, cw=True):
    k = 0.5523 * r
    pts = [(0, -r), (k, -r, r, -k, r, 0), (r, k, k, r, 0, r), (-k, r, -r, k, -r, 0), (-r, -k, -k, -r, 0, -r)]
    if not cw:
        return (f"m 0 -{r} b -{k:.1f} -{r} -{r} -{k:.1f} -{r} 0 b -{r} {k:.1f} -{k:.1f} {r} 0 {r} "
                f"b {k:.1f} {r} {r} {k:.1f} {r} 0 b {r} -{k:.1f} {k:.1f} -{r} 0 -{r}")
    return (f"m 0 -{r} b {k:.1f} -{r} {r} -{k:.1f} {r} 0 b {r} {k:.1f} {k:.1f} {r} 0 {r} "
            f"b -{k:.1f} {r} -{r} {k:.1f} -{r} 0 b -{r} -{k:.1f} -{k:.1f} -{r} 0 -{r}")


RING = circle(44) + " " + circle(37, cw=False)
ICONS = {
    "check": RING + " m -19 1 l -12 -6 l -5 1 l 12 -17 l 19 -10 l -5 15",
    "bolt": RING + " m 8 -26 l -13 4 l -2 4 l -7 26 l 13 -7 l 2 -4 l -1 -4 l 8 -19",
    "clock": RING + " m -2.5 2.5 l -2.5 -22 l 2.5 -22 l 2.5 2.5 m -2.5 -2.5 l 17 -2.5 l 17 2.5 l -2.5 2.5",
    "bars": RING + " m -22 20 l -22 6 l -13 6 l -13 20 m -4.5 20 l -4.5 -6 l 4.5 -6 l 4.5 20 m 13 20 l 13 -22 l 22 -22 l 22 20",
}


def build_ass():
    sz = CFG["subtitle_safe_zone"]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter,48,&H00FFFFFF,&H000000FF,&H00141414,&H90000000,-1,0,0,0,100,100,0,0,1,3.6,2.4,2,{sz['margin_left']},{sz['margin_right']},{sz['margin_bottom']},1
Style: Title,Inter,64,&H00FFFFFF,&H000000FF,&H00141414,&H80000000,0,0,0,0,100,100,0,0,1,0,3,5,60,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []

    def d(layer, a, b, style, text):
        ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{text}")

    CX = W // 2
    for t in CFG["titles"]:
        a, b = t["start"], t["end"]
        fo = 600 if b < TOTAL - 0.1 else int((TOTAL - CFG["fade_out"]["video_start"]) * 1000)
        if t["type"] == "brand":
            y = t.get("y", 800)
            d(3, a, b, "Title", f"{{\\an5\\pos({CX},{y})\\fad(900,{fo})\\fnInter\\b1\\fs108\\fsp26\\t(0,2200,\\fsp14)\\bord2.5\\3c&H202020&\\shad3\\4a&H60&\\blur0.8}}{t['text']}")
            d(3, a + 0.25, b, "Title", f"{{\\an5\\pos({CX},{y + 72})\\fad(700,{fo})\\p1\\bord0\\shad0\\1c{ACCENT}\\fscx0\\t(0,1100,\\fscx100)}}m -70 0 l 70 0 l 70 5 l -70 5{{\\p0}}")
        elif t["type"] == "tagline":
            y = t.get("y", 950)
            d(3, a, b, "Title", f"{{\\an5\\move({CX},{y + 20},{CX},{y},0,700)\\fad(700,{fo})\\fnInter\\b1\\fs46\\bord2.2\\3c&H202020&\\shad2\\4a&H60&\\blur0.6}}" + "\\N".join(t["lines"]))
        elif t["type"] == "headline":
            sizev = t.get("size", 62)
            d(3, a, b, "Title", f"{{\\an5\\move({CX},{500},{CX},{480},0,650)\\fad(650,550)\\fnInter\\b1\\fs{sizev}\\bord2.4\\3c&H202020&\\shad3\\4a&H60&\\blur0.7}}{t['text']}")
            d(3, a + 0.15, b, "Title", f"{{\\an5\\pos({CX},{430})\\fad(650,550)\\p1\\bord0\\shad0\\1c{ACCENT}\\fscx0\\t(0,900,\\fscx100)}}m -40 0 l 40 0 l 40 4 l -40 4{{\\p0}}")
        elif t["type"] == "lower":
            y0 = 340
            d(3, a, b, "Title", f"{{\\an7\\pos(62,{y0})\\fad(500,{fo})\\p1\\bord0\\shad0\\1c{ACCENT}\\fscy0\\t(0,900,\\fscy100)}}m 0 0 l 6 0 l 6 300 l 0 300{{\\p0}}")
            ys = {"main": y0 - 6, "accent": y0 + 84, "sub": y0 + 160}
            for ln in t["lines"]:
                y = ys[ln["style"]]
                col = {"main": "&HFFFFFF&", "accent": ACCENT, "sub": "&HEDEDED&"}[ln["style"]]
                fn = "Inter\\b1"
                d(3, ln["at"], b, "Title", f"{{\\an7\\move(70,{y},88,{y},0,600)\\fad(600,{fo})\\fn{fn}\\fs{ln['size']}\\1c{col}\\bord2.2\\3c&H202020&\\shad2\\4a&H60&\\blur0.6}}{ln['text']}")
        elif t["type"] == "vision":
            d(3, a, b, "Title", f"{{\\an5\\pos({CX},450)\\fad(350,350)\\p1\\bord0\\shad0\\1c{ACCENT}\\fscx70\\fscy70\\t(0,500,\\fscx150\\fscy150)}}{ICONS[t['icon']]}{{\\p0}}")
            d(3, a, b, "Title", f"{{\\an5\\move({CX},610,{CX},590,0,500)\\fad(400,350)\\fnInter\\b1\\fs74\\bord2.6\\3c&H202020&\\shad3\\4a&H60&\\blur0.7}}{t['text']}")
    for text, a, b in cues():
        d(5, a, b, "Sub", f"{{\\fad(120,100)}}{text}")
    (WORK / "subs.ass").write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def build_srt():
    lines = []
    for i, (text, a, b) in enumerate(cues(), 1):

        def f(x):
            ms = round(x * 1000)
            return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
        lines.append(f"{i}\n{f(a)} --> {f(b)}\n{text.replace(chr(92) + 'N', chr(10))}\n")
    (OUT / "MakkaDev_SousTitres.srt").write_text("\n".join(lines), encoding="utf-8")


def build_gradient():
    from PIL import Image
    import numpy as np
    y = np.arange(H)[:, None].astype(float)
    top = np.clip((620 - y) / 620, 0, 1) ** 1.6 * 85
    bot = np.clip((y - 1000) / 920, 0, 1) ** 1.5 * 165
    a = np.repeat(np.clip(top + bot, 0, 255), W, axis=1).astype("uint8")
    img = np.zeros((H, W, 4), "uint8")
    img[..., 3] = a
    Image.fromarray(img, "RGBA").save(WORK / "gradient.png")


# ---------------------------------------------------------------- 3. assemblage
def assemble(shots, clips):
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    inputs += ["-loop", "1", "-framerate", FPS, "-i", WORK / "gradient.png"]
    g = len(clips)
    parts = []
    prev = "[0:v]"
    for i in range(1, len(clips)):
        offset = shots[i]["start"] - OV / 2
        label = f"[x{i}]"
        parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={OV}:offset={offset:.3f}{label}")
        prev = label
    fo = CFG["fade_out"]["video_start"]
    parts.append(f"{prev}[{g}:v]overlay=0:0:format=auto,ass=work/subs.ass:fontsdir=/usr/share/fonts,"
                 f"fade=t=out:st={fo}:d={TOTAL - fo},format=yuv420p[vout]")
    fc = WORK / "assemble.filtergraph"
    fc.write_text(";\n".join(parts), encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex_script", fc, "-map", "[vout]", "-t", TOTAL,
         "-r", FPS, "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
         "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-profile:v", "high", "-level", "4.1", WORK / "video_noaudio.mp4"])


# ---------------------------------------------------------------- 4. audio
def mix_audio():
    music = Path(args.music) if args.music else HERE / CFG["music"]["file"]
    if CFG["music"].get("generated") and not args.music and not music.exists():
        run([sys.executable, "-I", HERE / "scripts" / "music.py", music, TOTAL])
    voice = HERE / CFG["voice"]["file"]
    ms = CFG["fade_out"]["music_start"]
    voice_ok = voice.exists() and not args.no_voice
    music_in = ["-i", music]
    fg = []
    if voice_ok:
        fg.append(f"[0:a]highpass=f=70,adelay={int(VOFF * 1000)}|{int(VOFF * 1000)},apad=whole_dur={TOTAL},"
                  "aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][vsc]")
    fg.append("[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-11dB,"
              f"volume='1+0.9*clip((2.0-t),0,1)+1.1*clip((t-{VOFF + 52.3 - 0.8}),0,1)':eval=frame,"
              f"afade=t=out:st={ms}:d={TOTAL - ms}[mu]")
    if voice_ok:
        fg.append("[mu][vsc]sidechaincompress=threshold=0.015:ratio=9:attack=40:release=700:makeup=1[md]")
        fg.append("[vo]acompressor=threshold=-21dB:ratio=2.2:attack=8:release=140:makeup=2[voc]")
        fg.append("[voc][md]amix=inputs=2:duration=longest:normalize=0,"
                  f"loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,atrim=0:{TOTAL}[aout]")
    else:
        fg.append(f"[mu]loudnorm=I=-18:TP=-1.5:LRA=9,aresample=48000,atrim=0:{TOTAL}[aout]")
    fgf = WORK / "audio.filtergraph"
    fgf.write_text(";\n".join(fg), encoding="utf-8")
    ins = (["-i", voice] if voice_ok else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]) + music_in
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex_script", fgf, "-map", "[aout]", "-t", TOTAL,
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", WORK / "audio.m4a"])
    return voice_ok


# ---------------------------------------------------------------- 5. export
def export_timeline(shots, voice_ok):
    tl = {
        "projet": "MakkaDev - vidéo institutionnelle (déplacement ministère des Finances, appel d'offres)",
        "format": {"largeur": W, "hauteur": H, "fps": FPS, "codec_video": "H.264", "codec_audio": "AAC"},
        "duree_totale_s": TOTAL,
        "transition": {"type": "fondu enchaîné", "duree_s": OV, "centre": "sur la coupe"},
        "voix_off": {"fichier": CFG["voice"]["file"], "debut_s": VOFF, "integree": voice_ok},
        "musique": {"fichier": CFG["music"]["file"], "generee_par_script": CFG["music"].get("generated", False),
                    "baisse_sous_la_voix": True, "fondu_sortie_debut_s": CFG["fade_out"]["music_start"]},
        "audio_original_des_videos": "coupé (non utilisé)",
        "plans": [
            {"n": s["index"] + 1, "scene": s["scene"], "debut_s": s["start"], "fin_s": s["end"],
             "duree_s": round(s["end"] - s["start"], 3), "source": CFG["sources"][s["src"]],
             "coupe_source_debut_s": round(s["ss"], 3), "coupe_source_fin_s": round(s["ss"] + s["dur"] * s["speed"], 3),
             "vitesse": s["speed"], "stabilisation": "vidstab", "transition_entrante": None if s["index"] == 0 else "fondu 0.4 s",
             "note": s["note"]} for s in shots],
        "textes": CFG["titles"],
        "sous_titres": [{"debut_s": round(a, 2), "fin_s": round(b, 2), "texte": t.replace("\\N", " ")}
                        for t, a, b in cues()],
    }
    (OUT / "MakkaDev_Timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    shots = plan_shots()
    print(f"{len(shots)} plans ; rendu des plans…")
    with ThreadPoolExecutor(max_workers=3) as ex:
        clips = list(ex.map(render_clip, shots))
    build_ass()
    build_srt()
    build_gradient()
    print("assemblage vidéo…")
    assemble(shots, clips)
    print("mixage audio…")
    voice_ok = mix_audio()
    final = OUT / "MakkaDev_Video_Finale.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", WORK / "video_noaudio.mp4", "-i", WORK / "audio.m4a", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", "-shortest", final])
    export_timeline(shots, voice_ok)
    print("terminé :", final)


if __name__ == "__main__":
    main()
