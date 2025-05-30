# Pleasanter on Render.com

このプロジェクトは、PleasanterをRender.comにデプロイするためのセットアップです。

## 機能

- PostgreSQLデータベースの自動セットアップ
- Pleasanterロール（Owner/User）の自動作成
- Extended SQLsの自動配置
- Render.comでの自動デプロイ

## セットアップ手順

### 1. 環境変数設定

`.env.template`を参考に`.env`ファイルを作成：

```bash
cp .env.template .env
```

必要な環境変数を設定してください：
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `OWNER_PASSWORD`
- `USER_PASSWORD`

### 2. データベース初期化

```bash
python src/main.py
```

### 3. Pleasanter初期化

```bash
docker compose -f docker-compose-codedefiner.yaml run --rm codedefiner _rds /l "ja" /z "Asia/Tokyo"
```

## カスタムDockerイメージ

このプロジェクトでは、`extended_sqls/`フォルダの内容を自動的に`/app/App_Data/Parameters/ExtendedSqls/`にコピーするカスタムDockerイメージを使用します。

### Extended SQLs

`extended_sqls/`フォルダに以下の形式でファイルを配置：

- `*.json` - Extended SQL設定ファイル
- `*.sql` - SQLクエリファイル

例：
```
extended_sqls/
├── DeletedBinariesOnUpdatedDelete.json
└── DeletedBinariesOnUpdatedDelete.json.sql
```

### ローカルビルド（オプション）

```bash
docker build -t pleasanter-custom .
docker run -p 8080:80 pleasanter-custom
```

## デプロイ

Render.comでの自動デプロイは`render.yaml`の設定に基づいて実行されます。

## トラブルシューティング

### データベース接続エラー
- 環境変数の設定を確認
- PostgreSQLサーバーの稼働状況を確認

### Extended SQLs が反映されない
- Dockerビルドが正常に完了しているか確認
- ファイルパーミッションを確認
