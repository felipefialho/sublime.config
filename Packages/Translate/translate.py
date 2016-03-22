# coding: utf8
# laputa

import sublime, sublime_plugin
import os
import stardict
import netdict
import parse


setting = sublime.load_settings('translate.sublime-settings')
pkgpath = sublime.packages_path()
dicpath = setting.get('dictdir')
dicpath = os.path.join(pkgpath, dicpath)
dic     = stardict.Dict(dicpath)
history = setting.get('history', False)


class LocalfileTranslateCommand(sublime_plugin.TextCommand):
    def show(self, items, count=None):
        if count and len(items) > count:
            items = items[:count]
            items.append('more..')
        self.view.window().show_quick_panel(items, self.on_done)

    def on_done(self, arg):
        if arg != -1:
            if arg == self.count:
                self.show(self.tetc)
            elif arg == self.count + 1:
                pass
        else:
            pass

    def run(self, edit):
        region = self.view.sel()[0]
        self.symbol = self.get_symbol(region).lower()
        self.tetc = self.query(self.symbol)
        self.count = setting.get('maxline', 4)
        self.show(self.tetc, self.count)

    def get_symbol(self, region):
        if region.begin() != region.end():
            return self.view.substr(region)            

        point  = region.begin()
        region = self.view.word(point)
        symbol = self.view.substr(region)

        point  = point - region.begin()
        end = region.end() - region.begin() + 1
        pos = symbol[:point].rfind('_')
        begin = 0 if pos == -1 else pos + 1
        pos = symbol[point:].find('_')
        end = end if pos == -1 else pos + point

        return symbol[begin:end]

    def query(self, word):
        text = dic.query(word)
        if not setting.get('store_index_in_memory', False):
            dic.release()        
        res = parse.parse_langdao(text)
        return res

class NetworkTranslateCommand(LocalfileTranslateCommand):
    def query(self, word, maxline=None):
        user_agent = setting.get('user_agent', 'sublime plugin')
        return netdict.qqdict(word, user_agent)

class HistoryTranslateListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        region = view.word(view.sel()[0])
        symbol = view.substr(region).lower()
        if history:      
            view.set_status('-', u'[ 中 ]')
