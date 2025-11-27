---
description: バックエンドのコードレビュー、ruffチェック、pytestを実行
---

# バックエンドレビューコマンド

以下の手順でバックエンドコードの品質チェックを行ってください：

## 1. ドキュメント確認

まず上位階層のdocsフォルダを読んで、アーキテクチャを理解してください：

- `../docs/README.md` - プロジェクト概要
- `../docs/architecture.puml` - ローカル環境アーキテクチャ（FastAPI + ARQ + Redis）
- `../docs/architecture-gcp.puml` - GCP本番環境アーキテクチャ（Cloud Tasks + Cloud Run Functions）

## 2. Ruff（リンター＆フォーマッター）

```bash
cd C:\workspace\app-template\backend
uv run ruff check .
uv run ruff format --check .
```

問題がある場合は自動修正：

```bash
uv run ruff check --fix .
uv run ruff format .
```

## 3. Pytest（テスト）

```bash
uv run pytest -v
```

## 4. コードレビュー

上記のチェックを実行した後、以下の観点でコードをレビューしてください：

### アーキテクチャ確認

- `docs/architecture.puml` と `docs/architecture-gcp.puml` のアーキテクチャに沿っているか
- レイヤー分離（routes → services → repositories）が守られているか
- TaskQueue抽象化（ARQ/GCP）が適切に使われているか

### コード品質

- 型ヒントが適切に付与されているか
- 非同期処理（async/await）が正しく使われているか
- エラーハンドリングが適切か
- SQLModelの使い方が適切か

### セキュリティ

- 入力バリデーションが行われているか
- SQLインジェクション対策がされているか
- 認証・認可の確認

レビュー結果を報告してください。
