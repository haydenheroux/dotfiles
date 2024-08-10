PS1='%B%F{blue}%~%f%b '

export _JAVA_AWT_WM_NONREPARENTING=1
export COLORTERM=truecolor

bindkey "^[[H"  beginning-of-line
bindkey "^[[4~" end-of-line
bindkey "^[[3~" delete-char

export PATH=$PATH:$HOME/go/bin

alias ls="exa -s type"
alias bq="batquery /sys/class/power_supply/BAT1/"
alias light="sudo light /sys/class/backlight/amdgpu_bl1/"
