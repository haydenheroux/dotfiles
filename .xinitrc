#!/bin/sh

xrdb ~/.Xresources
light 0
sh -c ~/.fehbg
# sh -c ~/dotfiles/bin/calibrate

dunst &
dwmblocks &
dwm
