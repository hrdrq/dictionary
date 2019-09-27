# 個人用辞書サーバとツール

## 機能
- 検索
  - 日本語意味：Wサイトの情報を取得
  - 中国語意味：Hサイトの情報を取得
  - 例文：Yサイトの情報を取得
  - 音声：NサイトとFサイトの音声ファイルを取得
  - 画像：googleの画像検索を利用
  - 重複処理：同じ単語は情報取得しない
  - マージ処理：同じ読み方の単語をマージできる
- 保存
  - 取得した情報をMySQLに保存
  - 画像と音声はAWS S3に保存
- Chrome拡張機能
  - UIをChrome拡張機能に入れ、任意のウェブサイトを見るとき、ショートカットで単語を検索できる
- エクスポート
  - MySQLの新しいデータや更新されたデータをエクスポートし、勉強用アプリにインポートする


*/1 * * * * ps ax |grep -v grep | grep server.py || /usr/bin/python3 /home/ubuntu/dictionary/server/server.py
