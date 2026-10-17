#!/usr/bin/env bash
# Local static-image + original recording + BGM compositor, not avatar generation.
set -euo pipefail
if [[ $# -ne 4 ]]; then
  echo 'Usage: bash compose-local.sh avatar-image voice-recording music-file output.mp4' >&2
  exit 2
fi
avatar_path=$1
voice_path=$2
music_path=$3
output_path=$4
for input_path in "$avatar_path" "$voice_path" "$music_path"; do
  [[ -f "$input_path" ]] || { echo 'Input file missing.' >&2; exit 2; }
done
[[ ! -e "$output_path" ]] || { echo 'Output exists; choose a new filename.' >&2; exit 2; }
ffmpeg -hide_banner -loglevel error -loop 1 -framerate 24 -i "$avatar_path" \
 -i "$voice_path" -stream_loop -1 -i "$music_path" \
 -filter_complex '[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0x142440,setsar=1[v];[1:a]aresample=48000,apad,volume=1[voice];[2:a]aresample=48000,volume=0.12[music];[voice][music]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,afade=t=out:st=14:d=1[a]' \
 -map '[v]' -map '[a]' -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -movflags +faststart -t 15 -n "$output_path"
