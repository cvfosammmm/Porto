#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

from result_factory.result_error.result_error import ResultError
from result_factory.result_image.result_image import ResultImage
from result_factory.result_html.result_html import ResultHtml
from result_factory.result_markdown.result_markdown import MarkdownResult
from result_factory.result_text.result_text import ResultText


class ResultFactory():

    def __init__(self):
        pass

    def get_error_from_result_message(self, result_message):
        return ResultError(
            result_message['content'].get('ename', ''),
            result_message['content'].get('evalue', ''),
            result_message['content'].get('traceback', '')
        )

    def get_error_from_nbformat_dict(self, nbformat_dict):
        return ResultError(
            nbformat_dict.get('ename', ''),
            nbformat_dict.get('evalue', ''),
            nbformat_dict.get('traceback', '')
        )

    def get_result_from_blob(self, blob):
        text = blob.get('text/plain', None)
        image = blob.get('image/png', None)
        html = blob.get('text/html', None)

        if image != None:
            return ResultImage(image)
        elif html != None:
            return ResultHtml(html)
        elif text != None:
            return ResultText(text)
        else:
            print(blob)

    def get_markdown_result_from_blob(self, blob):
        return MarkdownResult(blob)


