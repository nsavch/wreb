# WREB - Web Regular Expression Builder
# Copyright (C) 2008-2011  Nickolay S. Savchenko <nsavch@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django import template
from django.utils.html import escape

register = template.Library()

@register.inclusion_tag('wreb/result.html')
def match_result(matches):
    return {'matches' : matches}


def prepare(s):
    """Highlight spaces, lineends and tabs in string s"""
    s = escape(s)
    s = s.replace(' ', '<span class="whitespace">_</span>')
    s = s.replace('\n', '<span class="lineend">&crarr;\r\n</span>')
    s = s.replace('\t', '<span class="tab"> -> </span>')
    return s


def span(s, class_):
    return '<span class="%s">%s</span>' % (class_, prepare(s))


def show_groups_helper(matches):
    answ = []
    s = matches[0].string
    for match in matches:
        if match.group(0) == '': # Handle the case with empty regex
            unmatched_left = s
            unmatched_right = s = ''
        else:
            unmatched_left, s, unmatched_right = s.partition(match.group(0))
        answ += [span(unmatched_left, 'unmatched')]
        for group in match.groups():
            if group is not None:
                left, sep, right = s.partition(group)
                answ.append(span(left, 'match'))
                answ.append(span(sep, 'groupmatch'))
                s = right
        answ.append(span(s, 'match'))
        s = unmatched_right
    answ.append(span(unmatched_right, 'unmatched'))
    answ = ''.join(answ)
    return answ


@register.simple_tag
def show_groups(match):
    return show_groups_helper(match)
