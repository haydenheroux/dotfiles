export _JAVA_AWT_WM_NONREPARENTING=1
export COLORTERM=truecolor

bindkey "^[[H"  beginning-of-line
bindkey "^[[4~" end-of-line
bindkey "^[[3~" delete-char

export PATH=$PATH:$HOME/go/bin

alias ls="exa -s type"
alias bq="batquery -ip /sys/class/power_supply/BAT1/"
alias light="sudo light /sys/class/backlight/amdgpu_bl1/"

setopt PROMPT_SUBST
source /usr/share/git/git-prompt.sh
PS1='$(__git_ps1 | sed "/./s/^[[:space:]]*\(.*\)$/\1 /")%B%F{blue}%~%f%b '
