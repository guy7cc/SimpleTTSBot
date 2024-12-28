# SimpleTTSBot
[COEIROINK](https://coeiroink.com/)と併用して動くDiscord Botのスクリプトです。このプロジェクトはMIT Licenseの下で公開されています。

## 参考にしたサイト様
[自分の声でDISCORDの読み上げBOTを作成[COEIROINK]](https://note.com/aka7004/n/n235d251f9da3) - 部分的なコードサンプルとアイデア

## 使い方
まず、リポジトリをクローンします。  
次に、settings.pyを編集し、変数TOKENにDiscord Botのトークンの文字列を代入します。  
また、COEIROINKのモデルを追加する場合は、models.pyのModels列挙型に、任意の名前とモデルのスタイルIDの組み合わせでメンバーを追加します。
## 実行方法
Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-1018-oracle aarch64)、python3.8.10で動作が保障されています。asdfなどで当該バージョンのpythonをインストールした後、プロジェクトディレクトリ上で以下のコマンドを実行してください。
```
python -m venv venv
source ./venv/bin/activate
python -m pip install --upgrade pip
python -m pip install coloredlogs requests discord.py
python program.py
```
