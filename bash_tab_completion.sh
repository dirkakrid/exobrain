_exobrain_walkdir() {
	local namestart="$1"
	local dir="$2"

	# Append / to directories to get tab completions of the files inside
	if [ -d "$dir/$namestart" ]; then
		namestart="$namestart/"
	fi

	finddir="$(dirname "${namestart%%/*}")"
	finddir="${finddir:-.}"
	basename="${namestart##*/}"

	cd "$dir"

	(
		find "$finddir" -name "$basename*" -a \! -path '*.git*' | sed 's!./!!'
		find "$finddir" -type f -name "$basename*" -a \! -path '*.git*' | sed 's!./!!' | xargs basename -a 2> /dev/null
	) | sort -u
}

_TabComplete_Exobrain () {
	local cur="${COMP_WORDS[COMP_CWORD]}"
	COMPREPLY=( $(compgen -W "$(_exobrain_walkdir "$cur" "$EXOBRAIN_ROOT")" "$cur" ) )
}

complete -F _TabComplete_Exobrain -o filenames exobrain
