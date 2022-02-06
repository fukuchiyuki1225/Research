# 卒業論文スタイルファイル

卒業論文をpLaTeXを用いて作成する人のためのスタイルファイルです．
主に，和歌山大学システム工学部の社会情報学メジャーに所属する学生向けです．

本リポジトリに含まれるファイルは以下の通りです．
- [wuse_thesis.sty](wuse_thesis.sty): 卒論／修論用スタイルファイル
- [wuse_resume.sty](wuse_resume.sty): レジュメ用スタイルファイル

また，上記スタイルファイルを使用したサンプルとして以下を用意しています．
- [thesis_sample.tex](thesis_sample.tex): 卒論サンプル
- [master_sample.tex](master_sample.tex): 修論サンプル
- [resume_sample.tex](resume_sample.tex): 卒論用レジュメサンプル
 
## コンパイル方法

スタイルファイルwuse_thesis.styとサンプル卒論ファイルthesis_sample.texを同じディレクトリに置き，thesis_sample.texを`platex`でコンパイルしてください（必要に応じて複数回実行してください）．

    $ platex thesis_sample.tex

## 卒業論文の表紙について

タイトルページ（表紙）を生成するため，最初に以下の情報を記述してください．

- タイトル `\title`
- 氏名 `\author`
- 学位
  - 学士 `\bachelor`
  - 修士 `\master`
- 所属 `\department`
- 学生番号 `\sutudentid`
- 卒業年度 `\gyear`
- 提出日 `\date`

## 出力例

[thesis_sample.pdf](thesis_sample.pdf)は，thesis_sample.texをコンパイルしたthesis_sample.dviから`dvipdfmx`によりPDF化した例です．

    $ dvipdfmx thesis_sample.dvi
