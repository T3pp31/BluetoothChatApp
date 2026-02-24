# BluetoothChatApp — React Native 移行計画

## 概要

Python (PySimpleGUI + socket) で構築された既存の Bluetooth チャットアプリを、
React Native (Expo Development Build) + BLE に移行し、iOS / Android のクロスプラットフォーム対応を実現する。

---

## 技術選定

| カテゴリ | 選定 | 理由 |
|---------|------|------|
| フレームワーク | **Expo (Development Build)** | EAS Build/Update 対応、BLE プラグインあり、OTA アップデート可能。Expo Go では BLE 不可だが dev build なら使用可 |
| BLE ライブラリ | **react-native-ble-plx** (v3.5+) | 週90K DL、マルチデバイス対応、MTU交渉、Expo config plugin あり |
| ナビゲーション | **React Navigation v7** (Native Stack) | 公式推奨、安定、パフォーマンス良好 |
| 状態管理 | **Zustand v5** | 軽量、BLE ステートをグローバル管理するのに最適、ボイラープレート不要 |
| チャット UI | **react-native-gifted-chat** (v3.3+) | メッセージバブル・入力欄・スワイプ返信など標準機能が揃う |
| 画像選択 | **expo-image-picker** | Expo managed API、権限処理が簡潔 |
| 画像圧縮 | **react-native-image-resizer** | BLE 転送前に画像を 50KB 以下に圧縮（必須） |
| ファイルシステム | **react-native-blob-util** | ファイル読み書き、4095 バイトバッファチャンク対応 |
| 権限管理 | **react-native-permissions** | Android 12+ `BLUETOOTH_SCAN`/`BLUETOOTH_CONNECT` と iOS 対応 |
| テスト | **Jest** + **React Native Testing Library** | 標準的テストスタック |

### 主要依存パッケージ

```json
{
  "dependencies": {
    "expo": "~52.x",
    "react-native-ble-plx": "^3.5.0",
    "rxjs": "^7.x",

    "@react-navigation/native": "^7.x",
    "@react-navigation/native-stack": "^7.x",
    "react-native-screens": "^4.x",
    "react-native-safe-area-context": "^4.x",

    "zustand": "^5.x",

    "react-native-gifted-chat": "^3.3.2",
    "react-native-reanimated": "^3.x",
    "react-native-gesture-handler": "^2.x",

    "expo-image-picker": "~16.x",
    "react-native-image-resizer": "^3.x",
    "react-native-blob-util": "^0.21.x",

    "react-native-permissions": "^4.x",
    "@react-native-async-storage/async-storage": "^2.x"
  }
}
```

---

## BLE の制約と対策 (ファイル転送)

| 項目 | 値 |
|------|-----|
| デフォルト MTU | 23 バイト (有効ペイロード 20 バイト) |
| MTU 交渉後 (最大) | ~512 バイト (Android 最大 517) |
| iOS デフォルト交渉値 | ~185-187 バイト (自動交渉) |
| Android MTU 交渉 | `requestMTU()` を明示的に呼び出す必要あり (API 21+) |
| 実効スループット | 15-100 kbps (JS ブリッジのオーバーヘッドあり) |
| 転送方式 | チャンク分割 + ACK-per-chunk フロー制御 |

### 画像転送の手順

1. `react-native-image-resizer` で画像を圧縮 (目標: < 50KB)
2. Base64 エンコード (バッファサイズは 3 の倍数、例: 4095 バイト)
3. MTU - 3 バイトのチャンクに分割
4. チャンクごとに ACK を受けて順次送信
5. 受信側でチャンクを再結合

> **注意**: 100KB の圧縮 JPEG で約 8-60 秒かかる。非圧縮画像や動画は BLE では転送不可。

---

## プロジェクト構成 (feature-based)

```
BluetoothChatApp/
├── app.json                        # Expo config (BLE plugin 設定含む)
├── App.tsx
└── src/
    ├── features/
    │   ├── ble/
    │   │   ├── hooks/
    │   │   │   ├── useBLEScanner.ts      # デバイス探索ロジック
    │   │   │   └── useBLEConnection.ts   # 接続・切断管理
    │   │   ├── BLEDeviceList.tsx          # デバイス一覧画面
    │   │   └── BLEPermissions.ts         # BLE 権限リクエスト
    │   ├── chat/
    │   │   ├── hooks/
    │   │   │   └── useChatMessages.ts    # メッセージ送受信ロジック
    │   │   ├── ChatScreen.tsx            # チャット画面 (gifted-chat)
    │   │   ├── MessageBubble.tsx         # カスタムメッセージバブル
    │   │   └── ImageMessage.tsx          # 画像メッセージ表示
    │   └── settings/
    │       └── SettingsScreen.tsx        # 設定画面
    ├── services/
    │   ├── BLEService.ts                 # シングルトン BLE マネージャー
    │   ├── ChunkingService.ts            # MTU 対応チャンク分割
    │   └── PermissionsService.ts         # 統合権限管理
    ├── store/
    │   ├── useBLEStore.ts                # Zustand: デバイス/接続状態
    │   └── useChatStore.ts              # Zustand: メッセージ状態
    ├── navigation/
    │   └── AppNavigator.tsx              # React Navigation 設定
    ├── components/
    │   ├── Button.tsx                    # 共通ボタン
    │   └── ProgressBar.tsx              # 転送プログレスバー
    ├── utils/
    │   ├── base64.ts                     # Base64 エンコード/デコード
    │   └── bleProtocol.ts               # カスタムメッセージフレーミング
    ├── constants/
    │   └── ble.ts                        # UUID、MTU デフォルト、チャンクサイズ
    └── types/
        └── index.ts                      # TypeScript 型定義
```

### BLEService シングルトンパターン

`BLEService.ts` はシングルトンとして実装する。BLE マネージャーインスタンスが 1 つだけ存在することを保証し、複数のフックからインポートしても再初期化されない設計にする。

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
50KB 以上のファイルにはプログレスインジケーターと切断時リトライロジックを実装する。

---

## 権限設定

### Android (`app.json` または `AndroidManifest.xml`)

```xml
<!-- Android 12+ -->
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<!-- Android 11 以下 -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

### iOS (`app.json` の Expo config plugin)

```json
{
  "expo": {
    "plugins": [
      ["react-native-ble-plx", {
        "isBackgroundEnabled": false,
        "modes": ["central"],
        "bluetoothAlwaysPermission": "Allow $(PRODUCT_NAME) to connect to nearby devices via Bluetooth"
      }]
    ]
  }
}
```

---

## 実装フェーズ

### Phase 1: プロジェクト基盤
- [ ] Expo プロジェクト初期化 (`npx create-expo-app`)
- [ ] `react-native-ble-plx` インストール + `app.json` plugin 設定
- [ ] 依存パッケージインストール (Navigation, Zustand, gifted-chat 等)
- [ ] `npx expo prebuild` でネイティブコード生成
- [ ] ナビゲーション設定 + 画面骨格
- [ ] BLEService シングルトン実装 (デバイス探索 + 接続)

### Phase 2: チャット基本機能
- [ ] テキストメッセージ送受信 (BLE characteristic 経由)
- [ ] ChatScreen UI (`react-native-gifted-chat` 統合)
- [ ] Zustand でチャット状態管理 (`useChatStore`)
- [ ] BLE 接続状態管理 (`useBLEStore`)

### Phase 3: ファイル・画像転送
- [ ] ChunkingService 実装 (MTU 対応チャンク分割)
- [ ] 画像圧縮 + 送信 (`react-native-image-resizer` + `expo-image-picker`)
- [ ] ファイル受信 + 保存 (`react-native-blob-util`)
- [ ] 転送プログレスバー

### Phase 4: 品質向上
- [ ] エラーハンドリング (接続切断、タイムアウト、転送失敗リトライ)
- [ ] 権限リクエスト UI (BLE, カメラ, ストレージ)
- [ ] テスト追加 (Jest + RNTL)
- [ ] EAS Build 設定
