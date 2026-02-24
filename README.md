# BluetoothChatApp

Bluetooth経由でメッセージの送受信ができるデスクトップチャットアプリケーションです。

## 必要な環境

- Python 3.9以上
- Bluetooth対応のPC
- Poetry（パッケージ管理）

## セットアップ

### Poetryを使う場合

```bash
poetry install
```

### pipを使う場合

```bash
pip install -r requirements.txt
```

## アプリの起動

```bash
python main.py
```

起動すると「Bluetoothファイル送受信」というタイトルのGUIウィンドウが表示されます。

## 使い方

アプリには3つの主要な機能があります。

### 1. Bluetoothデバイスの検索

画面上部の **「検索」** ボタンをクリックすると、周囲のBluetoothデバイスを検索します。見つかったデバイスの一覧が画面下部の出力エリアに表示されます。

送信・受信に必要なBluetoothアドレスをここで確認してください。

### 2. メッセージの送信

1. 「送信したいアドレス」の横にある入力欄に、送信先の **Bluetoothアドレス** を入力します
2. その隣の入力欄に **送信したいメッセージ** を入力します
3. **「送信」** ボタンをクリックします

送信結果が出力エリアに表示されます。

### 3. メッセージの受信

1. 「受信したいアドレス」の横にある入力欄に、接続先の **Bluetoothアドレス** を入力します
2. その隣の入力欄に **Bluetoothチャンネル番号** を入力します
3. **「受信」** ボタンをクリックします

受信したデータが出力エリアに表示されます。

### 4. 終了

**「終了」** ボタンをクリックするか、ウィンドウを閉じるとアプリが終了します。

## プロジェクト構成

```
BluetoothChatApp/
├── main.py            # GUIアプリケーション本体
├── src/
│   ├── search.py      # Bluetoothデバイス検索モジュール
│   ├── send.py        # メッセージ送信モジュール
│   └── receive.py     # メッセージ受信モジュール
├── pyproject.toml     # Poetryプロジェクト設定
└── requirements.txt   # 依存パッケージ一覧
```

## 使用ライブラリ

- [PySimpleGUI](https://www.pysimplegui.org/) - GUIフレームワーク
- [Bleak](https://github.com/hbldh/bleak) - Bluetoothデバイス検索
- Python標準ライブラリ `socket` - Bluetooth RFCOMM通信
