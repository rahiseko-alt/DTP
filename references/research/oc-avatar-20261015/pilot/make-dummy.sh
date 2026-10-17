#!/usr/bin/env bash
# Geometry + test tones only. No AI, no person, no personal voice.
set -euo pipefail
pilot_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ffmpeg -hide_banner -loglevel error \
 -f lavfi -i 'color=c=0x142440:s=720x1280:r=24:d=15' \
 -f lavfi -i 'sine=frequency=440:duration=15' \
 -f lavfi -i 'sine=frequency=220:duration=15' \
 -filter_complex "[0:v]drawbox=x=270:y=500:w=180:h=180:color=0x2dc8d8:t=fill,drawtext=text='DUMMY - COMPOSITING TEST':fontcolor=white:fontsize=31:x=(w-tw)/2:y=120,drawtext=text='NO PERSON - NO AI GENERATION':fontcolor=white:fontsize=26:x=(w-tw)/2:y=180,drawtext=text='GEOMETRY AND TEST TONES ONLY':fontcolor=white:fontsize=25:x=(w-tw)/2:y=1000[v];[1:a]volume=0.5[voice];[2:a]volume=0.08[music];[voice][music]amix=inputs=2:duration=longest,afade=t=out:st=14:d=1[a]" \
 -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart -t 15 -y "$pilot_dir/dummy-compositing-only.mp4"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate -of json "$pilot_dir/dummy-compositing-only.mp4" > "$pilot_dir/ffprobe.json"
