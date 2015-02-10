# 時間割作成プログラム

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

## 参考

2015/2/11 に動かしてみた際の記録．


```
> git clone kmc.gr.jp:/git/seikichi/spring-camp-time-table.git
> cd spring-camp-time-table
> wget http://scip.zib.de/download/release/scip-3.1.0.linux.x86_64.gnu.opt.spx.zip
> unzip scip-3.1.0.linux.x86_64.gnu.opt.spx.zip
> python3 time_table.py --scip=./scip-3.1.0.linux.x86_64.gnu.opt.spx 2013.json
... (略)
objective value: 15.8273809523809
seikichi さんは tuda さんの →微分方程式で殴る(%%物理%%数学) という講座を見れません
seikichi さんは hanazuki さんの 未定 という講座を見れません
... (略)
|日程|時間|部屋1|講師|部屋2|講師|
|3/18 午後 1|90|→微分方程式で殴る(%%物理%%数学)|tuda||okabi|
|3/18 午後 2|90||lunan|物理学（相対性理論？）|astatine|
... (略)
```
