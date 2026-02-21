# OpenCode Office Setup Guide

ユーザーのプロダクトでOpenCode Officeを使用するための完全セットアップガイド。

## 📋 前提条件

- Python 3.11+
- Node.js 20+
- uv (Pythonパッケージマネージャー)
- OpenCodeがインストールされている

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/opencode-office.git
cd opencode-office
```

### 2. 依存関係のインストール

```bash
# すべての依存関係をインストール
make install
```

または個別に：

```bash
# バックエンド
cd backend
uv sync

# フロントエンド
cd ../frontend
npm install  # または bun install
```

### 3. 環境設定

バックエンドの設定ファイルを作成：

```bash
cd backend
cp .env.example .env
```

**重要な設定項目**:

```env
# OpenCodeサーバーのURL
OPENCODE_SERVER_URL=http://localhost:4096

# 認証が必要な場合
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=your-password

# OpenCodeアダプターを有効化
OPENCODE_ADAPTER_ENABLED=true
```

### 4. 起動

#### 方法A: tmuxを使用（推奨）

```bash
# プロジェクトルートで
make dev-tmux
```

これにより、バックエンドとフロントエンドが別のtmuxウィンドウで起動します。

#### 方法B: 個別に起動

**ターミナル1 - バックエンド**:
```bash
cd backend
make dev
```

**ターミナル2 - OpenCodeサーバー**:
```bash
opencode serve
```

**ターミナル3 - フロントエンド（開発用）**:
```bash
cd frontend
npm run dev  # または bun run dev
```

### 5. アクセス

ブラウザで以下のURLにアクセス：

- **開発モード**: [http://localhost:3000](http://localhost:3000)
- **静的ビルド**: [http://localhost:8000](http://localhost:8000)

## 🎯 使用方法

### シミュレーションでテスト（OpenCodeなし）

OpenCodeサーバーを起動せずに、ビジュアライザーをテストできます。

**UIから**:
- サイドバーの「シミュレーション開始」ボタンをクリック

**またはコマンドから**:
```bash
curl -X POST http://localhost:8000/api/v1/sessions/simulate
```

### OpenCodeと連携（本番使用）

1. **OpenCodeサーバーを起動**:
```bash
opencode serve --port 4096
```

2. **バックエンドを起動**（まだ起動していない場合）
3. **OpenCodeで作業を開始**:
   - 新しいセッションを作成
   - プロンプトを送信
   - ツールを実行

OpenCodeでの操作がリアルタイムでオフィス可視化されます！

## 🔧 詳細設定

### OpenCodeアダプターの有効/無効

`.env`ファイルで制御：

```env
# OpenCodeアダプターを無効化（シミュレーションのみ使用）
OPENCODE_ADAPTER_ENABLED=false

# 有効化
OPENCODE_ADAPTER_ENABLED=true
```

### AI要約の有効化（オプション）

```env
ENABLE_AI_SUMMARIES=true
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Gitステータス追跡

```env
# ポーリング間隔（秒）
GIT_POLL_INTERVAL=5
```

## 🐛 トラブルシューティング

### バックエンドが起動しない

```bash
# ポート使用状況を確認
lsof -i :8000
netstat -tln | grep 8000

# 別のポートを使用
make dev-backend PORT=8001
```

### フロントエンドがビルドできない

Node.jsバージョンを確認：

```bash
node --version  # 20+が必要
```

古い場合はアップグレード：
```bash
# nvmを使用
nvm install 20
nvm use 20

# またはlinuxbrew
brew install node@20
```

### OpenCode接続エラー

```bash
# OpenCodeサーバーのヘルスを確認
curl http://localhost:4096/global/health

# URLと認証設定を確認
cat backend/.env | grep OPENCODE
```

### シミュレーションが動作しない

```bash
# 手動でシミュレーションを実行
cd backend
uv run python ../scripts/simulate_events.py
```

### WebSocketエラー

ブラウザコンソールでエラーを確認：

```
[WS] Error: ...
```

**解決策**:
- バックエンドが稼働中か確認
- セッションIDが正しいか確認
- CORS設定を確認（通常デフォルトでOK）

## 📦 本番デプロイ

### 静的ビルド

```bash
make build-static
```

これにより、フロントエンドがビルドされ、`backend/static/`にコピーされます。

### Docker

```bash
# イメージをビルド
make docker-build

# コンテナーを起動
make docker-up

# ログを確認
make docker-logs
```

### 単一サーバーデプロイ

```bash
cd backend
make start
```

静的ファイルがバックエンドから配信されます。

## 🔍 監視とデバッグ

### バックエンドログ

```bash
# tmuxセッションにアタッチ
tmux attach -t opencode-office

# またはファイルから確認
tail -f /path/to/backend.log
```

### OpenCodeアダプターのデバッグ

```bash
# デバッグログを有効化
export LOG_LEVEL=DEBUG
cd backend
make dev
```

### セッション履歴

```bash
# すべてのセッションを表示
curl http://localhost:8000/api/v1/sessions

# セッションを削除
curl -X DELETE http://localhost:8000/api/v1/sessions/{session_id}

# データベースをクリア
curl -X DELETE http://localhost:8000/api/v1/sessions
```

## 🎨 カスタマイズ

### ホワイトボードモード

キーボードショートカット:
- `0-9`: ホワイトボードモードを切り替え
- `T`: Todoリスト
- `B`: バックグラウンドタスク

### デバッグモード

`D`キーでデバッグモードを有効化：
- `P`: エージェントパスを表示
- `Q`: キュースロットを表示
- `L`: フェーズラベルを表示

## 📚 追加リソース

- [OpenCodeドキュメント](https://opencode.ai/docs/)
- [API仕様](https://opencode.ai/docs/server/)
- [プラグインガイド](https://opencode.ai/docs/plugins/)

## 💡 ベストプラクティス

1. **開発**: tmuxを使用してバックエンドとフロントエンドを同時に監視
2. **テスト**: シミュレーションで機能を確認してからOpenCodeと連携
3. **モニタリング**: ログを定期的に確認
4. **バックアップ**: 重要なデータは定期的にバックアップ

## ❓ よくある質問

**Q: 静的ビルドと開発モードの違いは？**
A: 開発モードはホットリロード付きで、静的ビルドはバックエンドから配信される最適化ビルドです。

**Q: 複数のOpenCodeインスタンスを監視できますか？**
A: はい、`.env`の`OPENCODE_SERVER_URL`を変更して、複数のバックエンドインスタンスを起動できます。

**Q: どのツールが可視化されますか？**
A: bashコマンド、ファイル操作、Gitコマンドなど、OpenCodeで使用されるほとんどのツールが可視化されます。

**Q: プライベートなOpenCodeサーバーを使用できますか？**
A: はい、`OPENCODE_SERVER_URL`にURL、`OPENCODE_SERVER_USERNAME`と`OPENCODE_SERVER_PASSWORD`で認証を設定できます。
