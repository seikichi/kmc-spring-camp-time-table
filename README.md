# 時間割作成プログラム

## tl;dr

2013年度の時間割を決定するデモ

```
> docker build -t seikichi/spring-camp .
> cat 2013.json | docuer run --rm -i seikichi/spring-camp
```

## これは何?

KMC 春合宿の時間割を自動でいい感じに決めてくれるプログラムです．

## 準備

- python3
- [SCIP](http://scip.zib.de/#download)
  - ダウンロードしたファイルを適当な場所に展開すればOK
- 時間割の設定ファイル (同梱した `2013.json` を参照してそれっぽく作ってください)

## 実行

```
> python3 time_table.py --scip=path/to/scip/exec/file path/to/time/table/input.json
```
