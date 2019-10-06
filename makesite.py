#!/usr/bin/env python3

# Copyright (c) 2019 Susam Pal
# Licensed under the terms of the MIT License.

# This software is a derivative of the original makesite.py.
# The license text of the original makesite.py is included below.

# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Make static photo album with Python."""


import datetime
import glob
import json
import os
import re
import shutil
import sys

import yaml


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def make_album_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for albums."""
    items = []
    for post in posts:
        item_params = dict(params, **post)
        item = render(item_layout, **item_params)
        items.append(item)

    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)


def make_photo_list(album, photos, dst, list_layout, item_layout, **params):
    """Generate list page for photos in an album."""
    items = []
    for i, photo in enumerate(photos):
        item_params = dict(params, **photo)
        item_params['page'] = str(i + 1) + '.html'
        item = render(item_layout, **item_params)
        items.append(item)

    make_params = dict(params, **album)
    make_params.update({
        'root': '../',
        'class': 'photos',
        'content': ''.join(items),
        'total': len(photos),
    })

    dst_path = render(dst, **make_params)
    output = render(list_layout, **make_params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)


def make_page(dst, layout, **params):
    """Generate content (photo, text, etc.) page."""
    dst_path = render(dst, **params)
    output = render(layout, **params)
    log('Rendering page => {} ...', dst_path)
    fwrite(dst_path, output)


def make_photos(album, layout, **params):
    """Generate list page and photo pages for an album."""
    album_src_dir = os.path.join('content', album['input'])
    album_dst_dir = os.path.join('_site', album['album'])

    with open(os.path.join(album_src_dir, 'index.yaml')) as f:
        photo_index = yaml.safe_load(f)

    photos = []
    for i, photo in enumerate(photo_index):
        prev_page = str(i) + '.html'
        curr_page = str(i + 1) + '.html'
        next_page = str(i + 2) + '.html'

        prev_page = './' if i == 0 else prev_page
        next_page = './' if i == len(photo_index) - 1 else next_page

        photo_page_path = os.path.join(album_dst_dir, curr_page)
        img_src_path = os.path.join(album_src_dir, photo['photo'])
        img_dst_path = os.path.join(album_dst_dir, photo['photo'])

        date = datetime.datetime.strptime(photo['photo'][:8], '%Y%m%d')
        date = date.strftime('%d %b %Y')

        if photo.get('label') == 'face':
            license = 'All rights reserved'
        else:
            license = (
                'Licensed under '
                '<a href="https://creativecommons.org/licenses/by/4.0/">'
                'CC BY 4.0'
                '</a>'
            )

        photo_params = dict(params, **photo)
        photo_params.update({
            'root': '../',
            'class': 'photo',
            'prev': prev_page,
            'next': next_page,
            'index': i + 1,
            'total': len(photo_index),
            'album': album['title'],
            'date': date,
            'license': license,
        })

        photos.append(photo_params)

        make_page(photo_page_path, layout, **photo_params)
        shutil.copyfile(img_src_path, img_dst_path)
    return photos


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')

    # Default parameters.
    params = {
        'subtitle': ' - Sunaina Pai &amp; Susam Pal',
        'author': 'Sunaina Pai &amp; Susam Pal',
        'current_year': datetime.datetime.now().year,
    }

    page_layout = fread('layout/page.html')

    # Read index of albums.
    with open(os.path.join('content', 'index.yaml')) as f:
        album_index = yaml.safe_load(f)

    # Render album list page (home).
    list_layout = fread('layout/home/list.html')
    item_layout = fread('layout/home/item.html')
    list_layout = render(page_layout, content=list_layout)
    make_params = dict(params)
    make_params.update({
        'root': '',
        'title': 'Ungeeks',
        'class': 'albums',
    })
    make_album_list(album_index, '_site/index.html',
                    list_layout, item_layout, **make_params)

    # Render each photo list (album).
    post_layout = fread('layout/photo/post.html')
    list_layout = fread('layout/photo/list.html')
    item_layout = fread('layout/photo/item.html')
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)
    for i, album in enumerate(album_index):
        make_params = dict(params)
        make_params.update({
            'index': i + 1,
            'total': len(album_index),
        })
        photos = make_photos(album, post_layout, **make_params)
        make_photo_list(album, photos, '_site/{{ album }}/index.html',
                        list_layout, item_layout, **make_params)

    # Render about page.
    make_params = dict(params)
    make_params.update({
        'root': '../',
    })
    make_page('_site/about/index.html',
              page_layout,
              content=fread('content/about.html'),
              title='About Us', **make_params)


if __name__ == '__main__':
    main()
