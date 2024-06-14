#!/bin/sh

feh --bg-fill ~/.wallpaper.png

xinput --set-prop "$(xinput | grep Mouse | head -1 | cut -f2 | cut -d '=' -f2)" 'libinput Accel Profile Enabled' 0, 1

linux-discord-rich-presence -c ~/.config/rpc &
artha &
dwm &
dwmblocks
