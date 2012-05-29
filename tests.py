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

r"""
>>> from wreb.templatetags.wreb import prepare, show_groups_helper

Check all cases, which prepare should handle:
>>> prepare('the oeu  theu')
u'the<span class="whitespace">_</span>oeu<span class="whitespace">_</span><span class="whitespace">_</span>theu'
>>> prepare('the\nend\n')
u'the<span class="lineend">&crarr;\r\n</span>end<span class="lineend">&crarr;\r\n</span>'
>>> prepare('the\tend\t')
u'the<span class="tab"> -> </span>end<span class="tab"> -> </span>'
>>> prepare('&>><<')
u'&amp;&gt;&gt;&lt;&lt;'

Check mixed case:
>>> prepare('2 > 1\n\t& 3 < 4')
u'2<span class="whitespace">_</span>&gt;<span class="whitespace">_</span>1<span class="lineend">&crarr;\r\n</span><span class="tab"> -> </span>&amp;<span class="whitespace">_</span>3<span class="whitespace">_</span>&lt;<span class="whitespace">_</span>4'

Now, lets test form working:
>>> import wreb.forms
>>> form = wreb.forms.RegexForm({'regex' : 'hello', 'text' : 'hello, world' })
>>> show_groups_helper(form.match_result())
u'<span class="unmatched"></span><span class="match">hello</span><span class="unmatched">,<span class="whitespace">_</span>world</span>'

"""

import re

from django.test import TestCase
from django.test.client import Client

from wreb import forms
from wreb import views
import wreb.templatetags.wreb as templatetags


class FlagFieldTest(TestCase):

    def test_true_flag(self):
        f = forms.FlagField(flag=re.M)
        self.assertEquals(f.clean(True), re.M)

    def test_false_flag(self):
        f = forms.FlagField(flag=re.M)
        self.assertEquals(f.clean(False), 0)

class RegexFormTest(TestCase):

    def test_valid_regex(self):
        f = forms.RegexForm({'regex' : 'otehuaso',
                             'unicode' : True,
                             'multiline' : True})
        self.assertTrue(f.is_valid())
        r = f.cleaned_data['regex']
        self.assertTrue(isinstance(r, type(re.compile('tehou'))))
        self.assertEquals(r.pattern, 'otehuaso')
        self.assertEquals(r.flags, re.U + re.M)

    def test_invalid_regex(self):
        f = forms.RegexForm({'regex' : '(unbalanced parenthesis'})
        self.assertFalse(f.is_valid())
        self.assertEquals(f.errors['__all__'], [u'unbalanced parenthesis'])

    def test_valid_match(self):
        f = forms.RegexForm({'regex' : r'(abcd*)+', 'text' : 'abcdefabcdef'})
        self.assertTrue(f.match_result() is not None)

    def test_invalid_match(self):
        f = forms.RegexForm({'regex' : r'(abcd*)+', 'text' : 'abdefabdef'})
        self.assertTrue(f.is_valid())
        self.assertTrue(f.match_result() is None)

    def test_groups(self):
        f = forms.RegexForm({'regex' : r'(Abc\d+)efg(a*b+)',
                             'text' : 'Abc123efgbbb'})
        self.assertTrue(f.is_valid())
        for i in f.match_result():
            self.assertEquals(i.groups(), ('Abc123', 'bbb'))

    def test_multiple_matches(self):
        f = forms.RegexForm({'regex' : 'a', 'text' : 'toathahhau'})
        self.assertTrue(f.is_valid())
        num = 0
        for i in f.match_result():
            num += 1
        self.assertEquals(num, 3)

    def test_empty_group(self):
        f = forms.RegexForm({'regex': 'foo(.*)bar', 'text': 'foobar'})
        self.assertTrue(f.is_valid())
        self.assertEquals(f.match_result()[0].groups(), ('', ))

    def test_text_cleaning(self):
        f = forms.RegexForm({'text' :\
                                 'Aef\r\nteohu\nu\\noaeuht\\naoeu\\toeu\r\n'})
        self.assertEquals(f.is_valid(), True)
        self.assertEquals(f.cleaned_data['text'],\
                              'Aef\nteohu\nu\noaeuht\naoeu\toeu\n')


class BuildViewTest(TestCase):

    def test_response_code(self):
        response = self.client.get('/wreb/')
        self.assertEquals(response.status_code, 200)

    def test_template(self):
        response = self.client.get('/wreb/')
        self.assertTemplateUsed(response, 'wreb/build.html')
