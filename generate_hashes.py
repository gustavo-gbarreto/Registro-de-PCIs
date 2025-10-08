from flask_bcrypt import Bcrypt

# Crie uma instância temporária do Bcrypt. Não precisa do 'app' do Flask aqui.
bcrypt = Bcrypt()

# --- Defina aqui as senhas que você quer usar ---
password_admin = 'senhaadmin'
password_cliente = 'senhacliente'

# Gera os hashes para cada senha
hash_admin = bcrypt.generate_password_hash(password_admin).decode('utf-8')
hash_cliente = bcrypt.generate_password_hash(password_cliente).decode('utf-8')

# Imprime os hashes no terminal
print("\n--- COPIE E COLE OS HASHES ABAIXO NO SEU FICHEIRO user_database.py ---\n")
print(f"Hash para o usuário 'admin' (senha: {password_admin}):")
print(f"'{hash_admin}'")
print("\n-----------------------------------------------------------------------\n")
print(f"Hash para o usuário 'cliente1' (senha: {password_cliente}):")
print(f"'{hash_cliente}'")
print("\n")