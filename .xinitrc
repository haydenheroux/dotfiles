#!/bin/sh

xrdb ~/.Xresources
xcalib -d :0 -s -v fw13.icm
light 0
sh -c ~/.fehbg

dunst &
dwmblocks &
dwm
