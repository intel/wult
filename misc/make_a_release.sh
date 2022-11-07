#!/bin/sh -euf
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

PROG="make_a_release.sh"
BASEDIR="$(readlink -ev -- ${0%/*}/..)"

# Regular expression matching wult and ndl versions.
VERSION_REGEX='\([0-9]\+\)\.\([0-9]\+\)\.\([0-9]\+\)'

# File paths containing the version number that we'll have to adjust.
WULT_FILE="$BASEDIR/wulttools/_Wult.py"
NDL_FILE="$BASEDIR/wulttools/_Wult.py"
SPEC_FILE="$BASEDIR/rpm/wult.spec"

# The CHANGELOG.md file path.
CHANGELOG_FILE="$BASEDIR/CHANGELOG.md"

# Documentation file paths.
WULT_MAN_FILE="$BASEDIR/docs/man1/wult.1"
WULT_RST_FILE="$BASEDIR/docs/wult-man.rst"
NDL_MAN_FILE="$BASEDIR/docs/man1/ndl.1"
NDL_RST_FILE="$NDL_RST_FILE"

fatal() {
        printf "Error: %s\n" "$1" >&2
        exit 1
}

usage() {
        cat <<EOF
Usage: ${0##*/} <new_ver>

<new_ver> - new tool version to make in X.Y.Z format
EOF
        exit 0
}

ask_question() {
	local question=$1

	while true; do
		printf "%s\n" "$question (yes/no)?"
		IFS= read answer
		if [ "$answer" == "yes" ]; then
			printf "%s\n" "Very good!"
			return
		elif [ "$answer" == "no" ]; then
			printf "%s\n" "Please, do that!"
			exit 1
		else
			printf "%s\n" "Please, answer \"yes\" or \"no\""
		fi
	done
}

[ $# -eq 0 ] && usage
[ $# -eq 1 ] || fatal "insufficient or too many argumetns"

new_ver="$1"; shift

# Validate the new version.
printf "%s" "$new_ver" | grep -q -x "$VERSION_REGEX" ||
         fatal "please, provide new version in X.Y.Z format"

# Make sure that the current branch is 'master' or 'release'.
current_branch="$(git -C "$BASEDIR" branch | sed -n -e '/^*/ s/^* //p')"
if [ "$current_branch" != "master" -a "$current_branch" != "release" ]; then
	fatal "current branch is '$current_branch' but must be 'master' or 'release'"
fi

# Remind the maintainer about various important things.
ask_question "Did you run tests"
ask_question "Did you update 'CHANGELOG.md'"
ask_question "Did you specify pepc version dependency in 'setup.py' and 'wult.spec'"

# Change the tool version.
sed -i -e "s/^_VERSION = \"$VERSION_REGEX\"$/_VERSION = \"$new_ver\"/" "$WULT_FILE"
# Change RPM package version.
sed -i -e "s/^Version:\(\s\+\)$VERSION_REGEX$/Version:\1$new_ver/" "$SPEC_FILE"

# Update the man page.
argparse-manpage --pyfile "$WULT_FILE" --function _build_arguments_parser \
                 --project-name 'wult' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$WULT_MAN_FILE" \
                 --url 'https://github.com/intel/wult'
argparse-manpage --pyfile "$NDL_FILE" --function _build_arguments_parser \
                 --project-name 'wult' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$NDL_MAN_FILE" \
                 --url 'https://github.com/intel/wult'
pandoc --toc -t man -s "$WULT_MAN_FILE" -t rst -o "$WULT_RST_FILE"
pandoc --toc -t man -s "$NDL_MAN_FILE"  -t rst -o "$NDL_RST_FILE"

# Update debian changelog.
"$BASEDIR"/../pepc/misc/changelog_md_to_debian -o "$BASEDIR/debian/changelog" -p "wult" \
                                               -n "Artem Bityutskiy" \
                                               -e "artem.bityutskiy@intel.com" \
                                               "$CHANGELOG_FILE"

# Commit the changes.
git -C "$BASEDIR" commit -a -s -m "Release version $new_ver"

outdir="."
tag_name="v$new_ver"
release_name="Version $new_ver"

# Create new signed tag.
printf "%s\n" "Signing tag $tag_name"
git -C "$BASEDIR" tag -m "$release_name" -s "$tag_name"

if [ "$current_branch" = "master" ]; then
    branchnames="master and release brances"
else
    branchnames="release branch"
fi

cat <<EOF
To finish the release:
  1. push the $tag_name tag out
  2. push $branchnames branches out

The commands would be:
EOF

for remote in "origin" "upstream" "public"; do
    echo "git push $remote $tag_name"
    if [ "$current_branch" = "master" ]; then
        echo "git push $remote master:master"
        echo "git push $remote master:release"
    else
        echo "git push $remote release:release"
    fi
done

if [ "$current_branch" != "master" ]; then
    echo
    echo "Then merge the release branch back to master, and run the following commands:"

    for remote in "origin" "upstream" "public"; do
        echo "git push $remote master:master"
    done
fi
