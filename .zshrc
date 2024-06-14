# PS1='\033[34;1m\W \033[0m'
PS1='%B%F{blue}%~%f%b '

export _JAVA_AWT_WM_NONREPARENTING=1
export COLORTERM=truecolor
. "$HOME/.cargo/env"

export PATH=$PATH:$HOME/go/bin:$HOME/wpilib/2024/frccode/

# zsh key settings
bindkey  "^[[H"   beginning-of-line
bindkey  "^[[4~"   end-of-line
bindkey  "^[[3~"  delete-char

alias ls="exa -s type"
