# SimpleTTSBot
COEIROINKと併用して動くDiscord Botのスクリプトです。

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
