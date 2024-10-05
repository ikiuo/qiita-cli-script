# Qiita CLI 用ユーティリティ

Qiita CLI ディレクトリで使用します。

- qcarticle.py : 一覧表示など
- qcmdupdate.py : マークダウンの修正


## qcarticle.py

[PyYAML](https://pypi.org/project/PyYAML/)を使用するコマンドライン スクリプトです。

**実行例** : "SSE" タグの付いた記事の一覧を出力する

```
$ ./qcarticle.py --tag SSE
492a133d05edc55e4543.md  21163  2023/07/12 13:49:40  ---  'SSE4.2 拡張命令 CRC32 を使ってみる' (x86-64,crc,SSE,CRC32)
4a4f426f8245a00ef0d8.md  39961  2022/06/26 08:25:31  ---  'x86: SSE4.2 文字列検索用 PCMPESTRI / PCMPESTRM / PCMPISTRI / PCMPISTRM 命令' (C,C++,x86,SSE,SIMD)
ffd81d605343d2248f4c.md  94404  2021/09/04 05:33:23  ---  'x86 SSE: 逆数近似(_mm_rcp_ss : RCPSS) に使われている参照表を取り出す' (C,C++,アルゴリズム,x86,SSE)
```

<sub>qcarticle.py は Qiita CLI ディレクトリへシンボリック リンクしています</sub>

実行例の各列は

1. ファイル名
2. ファイル サイズ
3. 日付
4. 時刻
5. フラグ
6. タイトル

で、タイトルの後にタグです。

フラグは順に

- **i** : ignorePublish が true のとき
- **p** : private が true のとき
- **s** : slide が true のとき

となります。


## qcmdupdate.py

Qiita マークダウン仕様変更に追従するためのコマンド スクリプトです。

変更前

```
#タイトル1
##タイトル2
###タイトル3
```

変更後

```
# タイトル1
## タイトル2
### タイトル3
```
