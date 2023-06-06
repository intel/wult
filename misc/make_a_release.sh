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
WULT_FILE="$BASEDIR/wulttools/wult/_Wult.py"
NDL_FILE="$BASEDIR/wulttools/ndl/_Ndl.py"
EXERCISESUT_FILE="$BASEDIR/wulttools/exercisesut/_ExerciseSut.py"
SPEC_FILE="$BASEDIR/rpm/wult.spec"

# The CHANGELOG.md file path.
CHANGELOG_FILE="$BASEDIR/CHANGELOG.md"

# Documentation file paths.
WULT_MAN_FILE="$BASEDIR/docs/man1/wult.1"
WULT_RST_FILE="$BASEDIR/docs/wult-man.rst"
NDL_MAN_FILE="$BASEDIR/docs/man1/ndl.1"
NDL_RST_FILE="$BASEDIR/docs/ndl-man.rst"
EXERCISESUT_MAN_FILE="$BASEDIR/docs/man1/exercise-sut.1"
EXERCISESUT_RST_FILE="$BASEDIR/docs/exercise-sut-man.rst"

# Path to 'pepc' project sources.
PEPC_SRC_PATH="$BASEDIR/../pepc"
# Path to the CHANGELOG.md file of the 'pepc' project.
PEPC_CHANGELOG_MD="$PEPC_SRC_PATH/CHANGELOG.md"
# Path to the script converting CHANGELOG.md into debian changelog.
CHANGELOG_MD_TO_DEBIAN="$PEPC_SRC_PATH/misc/changelog_md_to_debian"
# Path to the script that prepares CHANGELOG.md for the release.
PREPARE_CHENGELOG_MD="$PEPC_SRC_PATH/misc/prepare_changelog_md"

fatal() {
        printf "$PROG: error: %s\n" "$1" >&2
        exit 1
}

usage() {
        cat <<EOF
Usage: ${0##*/} [optins] <new_ver>

<new_ver> - new tool version to make in X.Y.Z format. The X.Y.(Z+1) version
            will be used by default.

Options:
  -P, --pepc-version - version of the 'pepc' project this 'wult' version
                       requires.
EOF
}

fail_usage() {
    usage
    fatal "$1"
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

TEMP=$(getopt -n $PROG -o P:,h --long pepc-version:,help -- "$@" 2>&1) || fail_usage "$TEMP"
eval set -- "$TEMP"

pepcver=

if [ $# -gt 0 ]; then
    while true; do
        case "$1" in
        -P|--pepc-version)
            pepcver="$2"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --) shift; break
            ;;
        *) fail_usage "Unrecognized option: $1"
            ;;
        esac
        shift
    done
fi

if [ $# -eq 1 ]; then
    new_ver="$1"; shift
    # Validate the new version.
    printf "%s" "$new_ver" | grep -q -x "$VERSION_REGEX" ||
           fatal "please, provide new version in X.Y.Z format"
elif [ $# -eq 0 ]; then
    # The new version was not provided, increment the current version umber.
    sed_regex="^VERSION = \"$VERSION_REGEX\"$"
    ver_start="$(sed -n -e "s/$sed_regex/\1.\2./p" "$WULT_FILE")"
    ver_end="$(sed -n -e "s/$sed_regex/\3/p" "$WULT_FILE")"
    ver_end="$(($ver_end+1))"
    new_ver="$ver_start$ver_end"
else
    usage
fi

echo "New version: $new_ver"

# Validate the new version.
printf "%s" "$new_ver" | grep -q -x "$VERSION_REGEX" ||
         fatal "please, provide new version in X.Y.Z format"

if [ -n "$pepcver" ]; then
    echo "Required pepc version: $pepcver"

    # Validate the pepc dependency version.
    grep -q -x "^## \[$pepcver\] - .*" $PEPC_CHANGELOG_MD && exit_status=0 || exit_status="$?"
    if [ "$exit_status" == "1" ]; then
        fatal "bad pepc version \"$pepcver\": not found in \"$PEPC_CHANGELOG_MD\""
    elif [ "$exit_status" != "0" ]; then
        exit 1
    fi
fi

# Make sure that the current branch is 'main' or 'release'.
current_branch="$(git -C "$BASEDIR" branch | sed -n -e '/^*/ s/^* //p')"
if [ "$current_branch" != "main" -a "$current_branch" != "release" ]; then
	fatal "current branch is '$current_branch' but must be 'main' or 'release'"
fi

# Remind the maintainer about various important things.
ask_question "Did you run tests"
ask_question "Did you update 'CHANGELOG.md'"
ask_question "Did you specify the min. required pepc version"

if [ -n "$pepcver" ]; then
    # Update 'pepc' version dependency.
    sed -i -e "s/\(pepc\s*>=\s*\)$VERSION_REGEX/\1$pepcver/g" "$BASEDIR/setup.py"
    sed -i -e "s/\(pepc\s*>=\s*\)$VERSION_REGEX/\1$pepcver/g" "$BASEDIR/rpm/wult.spec"
    sed -i -e "s/^\(\s\+pepc\s*(>=\s*\)$VERSION_REGEX)/\1$pepcver)/g" "$BASEDIR/debian/control"
fi

# Update CHANGELOG.md.
"$PREPARE_CHENGELOG_MD" "$new_ver" "$CHANGELOG_FILE"
# Update debian changelog.
"$CHANGELOG_MD_TO_DEBIAN" -o "$BASEDIR/debian/changelog" -p "wult" -n "Artem Bityutskiy" \
                          -e "artem.bityutskiy@intel.com" "$CHANGELOG_FILE"

# Change the tool version.
sed -i -e "s/^VERSION = \"$VERSION_REGEX\"$/VERSION = \"$new_ver\"/" "$WULT_FILE"
# Change RPM package version.
sed -i -e "s/^Version:\(\s\+\)$VERSION_REGEX$/Version:\1$new_ver/" "$SPEC_FILE"

# Update the man page.
argparse-manpage --pyfile "$WULT_FILE" --function _build_arguments_parser \
                 --project-name 'wult' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$WULT_MAN_FILE" \
                 --url 'https://github.com/intel/wult'
argparse-manpage --pyfile "$NDL_FILE" --function _build_arguments_parser \
                 --project-name 'ndl' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$NDL_MAN_FILE" \
                 --url 'https://github.com/intel/wult'
argparse-manpage --pyfile "$EXERCISESUT_FILE" --function _build_arguments_parser \
                 --project-name 'wult' --author 'Artem Bityutskiy' \
                 --author-email 'dedekind1@gmail.com' --output "$EXERCISESUT_MAN_FILE" \
                 --url 'https://github.com/intel/wult'
pandoc --toc -t man -s "$WULT_MAN_FILE" -t rst -o "$WULT_RST_FILE"
pandoc --toc -t man -s "$NDL_MAN_FILE"  -t rst -o "$NDL_RST_FILE"
pandoc --toc -t man -s "$EXERCISESUT_MAN_FILE"  -t rst -o "$EXERCISESUT_RST_FILE"

# Commit the changes.
git -C "$BASEDIR" commit -a -s -m "Release version $new_ver"

outdir="."
tag_name="v$new_ver"
release_name="Version $new_ver"

# Create new signed tag.
printf "%s\n" "Signing tag $tag_name"
git -C "$BASEDIR" tag -m "$release_name" -s "$tag_name"

if [ "$current_branch" = "main" ]; then
    branchnames="main and release brances"
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
    if [ "$current_branch" = "main" ]; then
        echo "git push $remote main:main"
        echo "git push $remote main:release"
    else
        echo "git push $remote release:release"
    fi
done

if [ "$current_branch" != "main" ]; then
    echo
    echo "Then merge the release branch back to main, and run the following commands:"

    for remote in "origin" "upstream" "public"; do
        echo "git push $remote main:main"
    done
fi
