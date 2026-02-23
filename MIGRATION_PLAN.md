# BluetoothChatApp — React Native 移行計画

## 概要

Python (PySimpleGUI + socket) で構築された既存の Bluetooth チャットアプリを、
React Native + BLE に移行し、iOS / Android のクロスプラットフォーム対応を実現する。

---

## 技術選定

| カテゴリ | 選定 | 理由 |
|---------|------|------|
| フレームワーク | **React Native CLI** | BLE にはネイティブコードアクセスが必要。Expo Go では BLE 不可 |
| BLE ライブラリ | **react-native-ble-plx** | 週90K DL、マルチデバイス対応、MTU交渉、バックグラウンド動作(iOS) |
| ナビゲーション | **React Navigation v7** (Native Stack) | 標準的、安定、パフォーマンス良好 |
| 状態管理 | **Zustand** | 軽量、BLEステートをグローバル管理するのに最適 |
| 画像選択 | **react-native-image-picker** | bare RN プロジェクト向き |
| ファイルシステム | **react-native-fs** | ファイル読み書き・パス管理 |
| テスト | **Jest** + **React Native Testing Library** | 標準的テストスタック |

### BLE の制約と対策 (ファイル転送)

| 項目 | 値 |
|------|-----|
| デフォルト MTU | 23 バイト (有効ペイロード 20 バイト) |
| MTU 交渉後 (最大) | ~512 バイト (Android 最大 517) |
| iOS デフォルト交渉値 | ~185-187 バイト |
| 転送方式 | チャンク分割 + Write Without Response / Notifications |

画像・ファイルは MTU サイズに合わせてチャンク分割し、Write Without Response で送信する設計にする。

---

## プロジェクト構成 (予定)

```
BluetoothChatApp/
├── src/
│   ├── screens/
│   │   ├── DeviceScanScreen.tsx     # BLE デバイス探索画面
│   │   ├── ChatScreen.tsx           # チャット画面 (テキスト + ファイル)
│   │   └── SettingsScreen.tsx       # 設定画面
│   ├── services/
│   │   ├── BLEManager.ts           # BLE 接続・通信管理
│   │   └── FileTransferService.ts  # ファイルチャンク分割・転送プロトコル
│   ├── stores/
│   │   ├── bleStore.ts             # Zustand: BLE 接続状態
│   │   └── chatStore.ts            # Zustand: メッセージ・ファイル履歴
│   ├── components/
│   │   ├── MessageBubble.tsx       # メッセージ表示コンポーネント
│   │   ├── DeviceListItem.tsx      # デバイス一覧アイテム
│   │   ├── FileAttachment.tsx      # ファイル添付 UI
│   │   └── TransferProgress.tsx    # 転送プログレスバー
│   ├── protocols/
│   │   └── chatProtocol.ts         # ヘッダー定義 (タイプ/サイズ/ファイル名)
│   ├── navigation/
│   │   └── AppNavigator.tsx        # React Navigation 設定
│   └── utils/
│       └── permissions.ts          # BLE/カメラ権限管理
├── android/
├── ios/
├── App.tsx
├── package.json
└── tsconfig.json
```

---

## 転送プロトコル設計

### メッセージヘッダー (最初のチャンク)

```
[1 byte: type] [4 bytes: totalSize] [2 bytes: filenameLength] [N bytes: filename]
```

| type | 意味 |
|------|------|
| 0x01 | テキストメッセージ |
| 0x02 | 画像 |
| 0x03 | ファイル |

### データチャンク

```
[2 bytes: chunkIndex] [2 bytes: chunkSize] [N bytes: data]
```

受信側はチャンクを順番に再結合し、totalSize に達したら完了とする。

---

## 実装フェーズ

### Phase 1: プロジェクト基盤
- [ ] React Native CLI プロジェクト初期化
- [ ] 依存パッケージインストール
- [ ] ナビゲーション・画面骨格
- [ ] BLEManager サービス (デバイス探索 + 接続)

### Phase 2: チャット基本機能
- [ ] テキストメッセージ送受信
- [ ] ChatScreen UI (メッセージバブル)
- [ ] Zustand でチャット状態管理

### Phase 3: ファイル・画像転送
- [ ] 転送プロトコル実装 (チャンク分割)
- [ ] 画像選択 + 送信
- [ ] ファイル受信 + 保存
- [ ] プログレスバー

### Phase 4: 品質向上
- [ ] エラーハンドリング (接続切断、タイムアウト、転送失敗)
- [ ] 権限リクエスト (BLE, カメラ, ストレージ)
- [ ] テスト追加
