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

# 環境変数からパスワードを取得
OWNER_PASSWORD = os.getenv('OWNER_PASSWORD')
USER_PASSWORD = os.getenv('USER_PASSWORD')

# パスワードが設定されていない場合のデフォルト値
if not OWNER_PASSWORD:
    OWNER_PASSWORD = "yaf12345"
    print(f"警告: OWNER_PASSWORDが.envファイルに見つかりません。デフォルト値を使用: {OWNER_PASSWORD}")
else:
    print("OWNER_PASSWORDを.envファイルから読み取りました")

if not USER_PASSWORD:
    USER_PASSWORD = "y3d12345"
    print(f"警告: USER_PASSWORDが.envファイルに見つかりません。デフォルト値を使用: {USER_PASSWORD}")
else:
    print("USER_PASSWORDを.envファイルから読み取りました")

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
    
    # 必要なロールを定義
    roles_to_create = [
        {
            "name": "Implem.Pleasanter_Owner",
            "password": OWNER_PASSWORD,
            "login": True
        },
        {
            "name": "Implem.Pleasanter_User",
            "password": USER_PASSWORD,
            "login": True
        }
    ]
    
    # 各ロールを確認・作成
    for role in roles_to_create:
        role_name = role["name"]
        cursor.execute("SELECT rolname FROM pg_roles WHERE rolname = %s", (role_name,))
        role_exists = cursor.fetchone()
        
        if not role_exists:
            print(f"'{role_name}'ロールが存在しないため、作成します。")
            # ロール作成
            if role["login"]:
                cursor.execute(sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s VALID UNTIL 'infinity'").format(
                    sql.Identifier(role_name)
                ), (role["password"],))
            else:
                cursor.execute(sql.SQL("CREATE ROLE {}").format(
                    sql.Identifier(role_name)
                ))
            print(f"ロール'{role_name}'を作成しました。")
        else:
            print(f"'{role_name}'ロールは既に存在します。")
            
            # ログイン権限を確認・追加
            if role["login"]:
                cursor.execute("SELECT rolcanlogin FROM pg_roles WHERE rolname = %s", (role_name,))
                can_login = cursor.fetchone()[0]
                
                if not can_login:
                    print(f"'{role_name}'ロールにログイン権限を追加します...")
                    cursor.execute(sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD %s VALID UNTIL 'infinity'").format(
                        sql.Identifier(role_name)
                    ), (role["password"],))
                    print("ログイン権限を追加しました。")
                
                # パスワードを更新
                print(f"'{role_name}'ロールのパスワードを更新します...")
                cursor.execute(sql.SQL("ALTER ROLE {} WITH PASSWORD %s").format(
                    sql.Identifier(role_name)
                ), (role["password"],))
                print("パスワードを更新しました。")
        
        # 現在のユーザーにロールを付与
        cursor.execute(sql.SQL("GRANT {} TO {}").format(
            sql.Identifier(role_name),
            sql.Identifier(current_user)
        ))
        print(f"ロール'{role_name}'を'{current_user}'に付与しました。")
    
    # ロール間の権限設定
    print("ロール間の権限を設定しています...")
    try:
        # Implem.Pleasanter_OwnerにImplem.Pleasanter_Userを付与
        cursor.execute(sql.SQL("GRANT {} TO {}").format(
            sql.Identifier("Implem.Pleasanter_User"),
            sql.Identifier("Implem.Pleasanter_Owner")
        ))
        print("'Implem.Pleasanter_User'ロールを'Implem.Pleasanter_Owner'に付与しました。")
    except Exception as role_grant_error:
        print(f"ロール付与中にエラー（無視して続行）: {role_grant_error}")
    
    # データベース存在確認
    db_name = "Implem.Pleasanter"
    cursor.execute("SELECT datname FROM pg_database WHERE datname = %s", (db_name,))
    db_exists = cursor.fetchone()
    
    if not db_exists:
        print(f"'{db_name}'データベースが存在しないため、作成します。")
        # データベース作成
        cursor.execute(sql.SQL("CREATE DATABASE {} WITH OWNER = {}").format(
            sql.Identifier(db_name),
            sql.Identifier("Implem.Pleasanter_Owner")
        ))
        print(f"データベース'{db_name}'を作成しました。")
    else:
        print(f"'{db_name}'データベースは既に存在します。所有者を確認・更新します。")
        # データベースの所有者を変更
        cursor.execute(sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
            sql.Identifier(db_name),
            sql.Identifier("Implem.Pleasanter_Owner")
        ))
        print(f"データベース'{db_name}'の所有者を'Implem.Pleasanter_Owner'に更新しました。")
    
    # データベースへのアクセス権設定
    print("データベースへのアクセス権を設定しています...")
    try:
        # Owner
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(db_name),
            sql.Identifier("Implem.Pleasanter_Owner")
        ))
        print("'Implem.Pleasanter_Owner'にデータベースの全権限を付与しました。")
        
        # User
        cursor.execute(sql.SQL("GRANT CONNECT, TEMPORARY ON DATABASE {} TO {}").format(
            sql.Identifier(db_name),
            sql.Identifier("Implem.Pleasanter_User")
        ))
        print("'Implem.Pleasanter_User'にデータベースの接続権限を付与しました。")
    except Exception as db_grant_error:
        print(f"データベース権限付与中にエラー（無視して続行）: {db_grant_error}")
    
    print("\n=== 設定情報 ===")
    print("作成または確認したロール:")
    for role in roles_to_create:
        masked_password = role['password'][:2] + '*' * (len(role['password']) - 2)
        print(f"  - {role['name']} (パスワード: {masked_password})")
    print(f"データベース: {db_name}")
    print("================\n")
    
    # 成功メッセージ
    print("PostgreSQLデータベースとロールの設定が完了しました。")
    print("次のコマンドを実行してImplem.Pleasanterの初期化を続行してください:")
    print("docker compose -f docker-compose-codedefiner.yaml run --rm codedefiner _rds /l \"ja\" /z \"Asia/Tokyo\" /f")
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    
finally:
    # 接続を閉じる
    if 'conn' in locals() and conn is not None:
        cursor.close()
        conn.close()
        print("PostgreSQL接続を閉じました。")
