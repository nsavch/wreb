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

import re

from django import forms

class FlagField(forms.BooleanField):

    def __init__(self, flag=0, **kwargs):
        self._flag = flag
        kwargs['required'] = False
        super(FlagField, self).__init__(**kwargs)

    def clean(self, value):
        v = super(FlagField, self).clean(value)
        if v:
            return self._flag
        else:
            return 0


class RegexForm(forms.Form):
    regex = forms.CharField(widget=forms.Textarea(attrs={'cols' : 80,
                                                         'rows' : 2}),
                            required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={'cols' : 80,
                                                        'rows' : 6}),
                           required=False)
    unicode = FlagField(re.U)
    multiline = FlagField(re.M)
    ignorecase = FlagField(re.I)
    dotall = FlagField(re.S)
    verbose = FlagField(re.X)

    def charfields(self):
        return [self['regex'], self['text']]

    def flagfields(self):
        return [self['unicode'],
                self['multiline'],
                self['ignorecase'],
                self['dotall'],
                self['verbose']]

    def clean_text(self):
        """Normalize text field.

        This includes converting dos line endings (which browsers use
        for some strange reasons).

        """
        return  self.cleaned_data['text'].\
                     replace('\r\n', '\n').\
                     replace(r'\n', '\n').\
                     replace(r'\t', '\t')

    def all_errors(self):
        return self.errors.get('__all__', '')

    def clean(self):
        flags = 0
        for f in self.fields:
            if isinstance(self.fields[f], FlagField):
                flags += self.cleaned_data[f]
        try:
            r = re.compile(self.cleaned_data['regex'], flags)
        except re.error, v:
            raise forms.ValidationError, v
        self.cleaned_data['regex'] = r

        return self.cleaned_data

    def match_result(self):
        if not self.is_valid():
            return None
        r = self.cleaned_data['regex']
        if not r.search(self.cleaned_data['text']):
            return None
        else:
            matches = []
            for i in r.finditer(self.cleaned_data['text']):
                matches.append(i)
            return matches
