export _JAVA_AWT_WM_NONREPARENTING=1
export COLORTERM=truecolor

bindkey "^[[H"  beginning-of-line
bindkey "^[[4~" end-of-line
bindkey "^[[3~" delete-char
bindkey "^[b" backward-word
bindkey "^[f" forward-word

export EDITOR="nvim"

setopt PROMPT_SUBST
source /usr/share/git/git-prompt.sh
PS1='%(1j.󰒲 .)$(__git_ps1 | sed "/./s/^[[:space:]]*\(.*\)$/\1 /")%B%F{blue}%~%f%b '

eval "$(zoxide init zsh)"
alias cd="z"
alias ls="exa -s type"
alias bq="batquery -ip /sys/class/power_supply/BAT1/"
alias light="sudo light /sys/class/backlight/amdgpu_bl1/"
alias start="startx"

autoload -Uz compinit
compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
source <(fzf --zsh)
# Default location for AUR install
source /usr/share/zsh/plugins/fzf-tab/fzf-tab.plugin.zsh
