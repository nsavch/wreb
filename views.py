# WREB - Web Regular Expression Builder
# Copyright (C) 2008  Nickolay S. Savchenko <nsavch@gmail.com>

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

import simplejson

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import Http404, HttpResponse

from wreb.forms import RegexForm

def build_regex(request):
    if request.method == 'POST':
        form = RegexForm(request.POST)
    else:
        form = RegexForm()
    return render_to_response('wreb/build.html', {'form': form},
                              RequestContext(request))

def ajax(request):
    if request.method != 'POST':
        raise Http404
    form = RegexForm(request.POST)
    html = render_to_string('wreb/ajax.html', {'form': form},
                            RequestContext(request))
    return HttpResponse(simplejson.dumps(dict(html=html)),
                        mimetype='application/json')
