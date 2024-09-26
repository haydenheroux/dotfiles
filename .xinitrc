#!/bin/sh

xrdb ~/.Xresources
xcalib -d :0 -s -v fw13.icm

dunst &
dwmblocks &
dwm
