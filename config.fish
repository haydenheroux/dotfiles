set -Ux _JAVA_AWT_WM_NONREPARENTING 1
set -Ux COLORTERM truecolor
set -Ux EDITOR nvim

bind \eOH beginning-of-line
bind \eOF end-of-line
bind \e\[3\~ delete-char

bind \eb backward-word
bind \ef forward-word

starship init fish | source
zoxide init fish | source

function cd
    z $argv
end

alias ls "eza -s type"

alias bq "batquery -ip /sys/class/power_supply/BAT1/"

alias light "sudo light /sys/class/backlight/amdgpu_bl1/"

alias start startx

# TODO Install fzf.fish
fzf --fish | source
