import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 接続情報を環境変数から取得
connection_params = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB')
}

# 接続情報を表示（パスワードは除く）
print("接続情報:")
for key, value in connection_params.items():
    if key != 'password':
        print(f"  {key}: {value}")

# PostgreSQLに接続
try:
    print("PostgreSQLデータベースに接続しています...")
    conn = psycopg2.connect(**connection_params)
    conn.autocommit = True  # 自動コミットを有効化
    cursor = conn.cursor()
    
    print("PostgreSQLデータベースに接続しました。")
    
    # 現在のユーザー名を取得
    cursor.execute("SELECT current_user")
    current_user = cursor.fetchone()[0]
    print(f"現在のユーザー: {current_user}")
    
    # 既存のロールを確認
    role_name = "Implem.Pleasanter_Owner"
    cursor.execute("SELECT rolname FROM pg_roles WHERE rolname = %s", (role_name,))
    role_exists = cursor.fetchone()
    
    if not role_exists:
        print(f"'{role_name}'ロールが存在しないため、作成します。")
        # ロール作成
        cursor.execute(sql.SQL("CREATE ROLE {} WITH NOLOGIN").format(
            sql.Identifier(role_name)
        ))
        print("ロールを作成しました。")
    else:
        print(f"'{role_name}'ロールは既に存在します。")
    
    # 現在のユーザーにロールを付与
    cursor.execute(sql.SQL("GRANT {} TO {}").format(
        sql.Identifier(role_name),
        sql.Identifier(current_user)
    ))
    print(f"ロールを'{current_user}'に付与しました。")
    
    # 成功メッセージ
    print("ロールの設定が完了しました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    
finally:
    # 接続を閉じる
    if 'conn' in locals() and conn is not None:
        cursor.close()
        conn.close()
        print("PostgreSQL接続を閉じました。")
