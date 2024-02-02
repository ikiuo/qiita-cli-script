#!/usr/bin/env python3

import collections
import functools
import os
import yaml  # pip: PyYAML
from datetime import datetime

QiitaArticleBriefBase = ('article', 'size', 'id', 'path', 'last', 'flags', 'org')
QiitaArticleBrief = collections.namedtuple('QiitaArticleBrief', QiitaArticleBriefBase)


class QiitaArticle:
    NOW = datetime(1970, 1, 1)
    NOWISO = str(NOW)

    def __init__(self, path):
        self.path = path
        self.stat = os.stat(path)

        with open(path) as ifp:
            self.file_lines = ifp.readlines()

        block_lno = []
        for lno in range(len(self.file_lines)):
            if self.file_lines[lno].split()[0] == '---':
                block_lno.append(lno)
                if len(block_lno) >= 2:
                    break
        if len(block_lno) < 2:
            raise ValueError(f'invalid format: {path}')
        self.header_lines = self.file_lines[block_lno[0]+1:block_lno[1]]
        self.article_lines = self.file_lines[block_lno[1]+1:]

        self.header = yaml.load(''.join(self.header_lines), Loader=yaml.Loader)

        self.size = self.stat.st_size
        self.ID = self.header.get('id', '')
        self.title = self.header.get('title', '')
        self.updated_at = self.header.get('updated_at', '')
        self.updated_at_dt = (datetime.fromisoformat(self.updated_at)
                              if self.updated_at else QiitaArticle.NOW)
        self.private = self.header.get('private')
        self.slide = self.header.get('slide')
        self.local = self.header.get('ignorePublish')
        self.orgurl = self.header.get('organization_url_name', '')
        self.tags = [str(s) for s in self.header.get('tags', [])]

    def __repr__(self):
        return ('QiitaArticle('
                f'path={repr(self.path)},'
                f' id={repr(self.ID)},'
                # f' stat={repr(self.stat)},'
                ' ...)')

    def getbrief(self):
        tfn = (lambda m: {False: '-', True: m, None: '?'})

        size = f'{self.size}'

        udt = self.updated_at_dt
        ymd = f'{udt.year:04}/{udt.month:02}/{udt.day:02}'
        hms = f'{udt.hour:02}:{udt.minute:02}:{udt.second:02}'
        last = f'{ymd} {hms}'

        local = tfn('i')[self.local]
        private = tfn('p')[self.private]
        slide = tfn('s')[self.slide]
        flags = f'{local}{private}{slide}'

        org = self.orgurl if self.orgurl else ''

        return QiitaArticleBrief(self, size, self.ID, self.path, last, flags, org)

    def getbriefwithlen(self):
        brief = self.getbrief()
        return QiitaArticleBrief(
            (0, brief[0]),
            *[(len(d or ''), d or '') for d in brief[1:]])


if __name__ == '__main__':
    import argparse
    import sys

    def main():
        ismdfile = (lambda path: os.path.splitext(path)[1] == '.md')

        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--reverse', action='store_true',
                            default=False, help='逆順ソート')
        parser.add_argument('-t', '--sort-updated', action='store_true',
                            default=False, help='updated_at でソート')
        parser.add_argument('-T', '--sort-title', action='store_true',
                            default=False, help='題名でソート')
        parser.add_argument('--sort-id', action='store_true',
                            default=False, help='id でソート')
        parser.add_argument('--no-title', action='store_false', dest='title',
                            default=True, help='題名の出力を抑制')
        parser.add_argument('--no-tags', action='store_false', dest='tags',
                            default=True, help='タグの出力を抑制')
        parser.add_argument('--id', action='store_true', dest='ID',
                            default=False, help='id を出力')
        parser.add_argument('--organization', action='store_true',
                            default=False, help='organization_url_name を出力')
        parser.add_argument('--tag', metavar='TAG', nargs='+', dest='tagfilter',
                            default=[], help='特定タグを出力')
        parser.add_argument('--taglist', action='store_true',
                            default=False, help='タグの一覧を出力')
        parser.add_argument('paths', metavar='PATH', nargs='*',
                            help='.md ファイルへのパス')
        args = parser.parse_args()

        files = args.paths
        if not files:
            os.chdir('public')
            files = filter(ismdfile, os.listdir())
        articles = list(map(QiitaArticle, files))

        if args.taglist:
            tags = functools.reduce(lambda p, v: p | set(v.tags), articles, set())
            print('タグ一覧:')
            print(' - ' + '\n - '.join(sorted(tags)))
            return

        ltcmp = (lambda b: -1 if b else 1)
        def article_cmp(lhs, rhs):
            if args.sort_updated and lhs.updated_at_dt != rhs.updated_at_dt:
                return ltcmp(str(lhs.updated_at_dt) < str(rhs.updated_at_dt))
            if args.sort_title and lhs.title != rhs.title:
                return ltcmp(lhs.title < rhs.title)
            if args.sort_id and lhs.ID != rhs.ID:
                return ltcmp(lhs.ID < rhs.ID)
            return ltcmp(lhs.path < rhs.path)
        sort_key = functools.cmp_to_key(article_cmp)

        articles = sorted(articles, key=sort_key, reverse=args.reverse)

        if args.tagfilter:
            tagfilter = (lambda a: sum(t in args.tagfilter for t in a.tags))
            articles = list(filter(tagfilter, articles))
        if not articles:
            print('記事がみつかりませんでした')
            return

        list_brief(args, articles)

    def list_brief(args, articles):
        colitem = [2, 0, 3, 4]
        if args.ID or args.sort_id:
            colitem.append(1)
        if args.organization:
            colitem.append(5)
        title_sep = '  '
        tag_sep = ' '

        briefs = [a.getbriefwithlen() for a in articles]
        columns = len(QiitaArticleBriefBase)
        colwidth = [[] for _ in range(columns)]
        for brief in briefs:
            for index in range(columns):
                colwidth[index].append(brief[index][0])
        colwidth = [max(w) for w in colwidth]
        colpad = [' ' * w for w in colwidth]

        blines = [[b[0][1], [f'{colpad[1]}{b[1][1]}'[-colwidth[1]:],
                             *[f'{b[n][1]}{colpad[n]}'[:colwidth[n]]
                               for n in range(2, columns)]]]
                  for b in briefs]
        for bline in blines:
            article = bline[0]
            line = '  '.join([*[bline[1][n] for n in colitem]])
            if args.title:
                line += title_sep + repr(article.title)
            if args.tags and article.tags:
                line += tag_sep
                line += '(' + ','.join(article.tags) + ')'
            print(line)

    sys.exit(main())
