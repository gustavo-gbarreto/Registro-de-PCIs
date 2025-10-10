from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# --- Coloque aqui a senha do NOVO utilizador ---
nova_senha = 'senha123'
nome_do_novo_utilizador = 'cliente2'

# Gera o hash para a nova senha
novo_hash = bcrypt.generate_password_hash(nova_senha).decode('utf-8')

# Imprime o hash no terminal
print("\n--- Hash para o novo utilizador ---")
print(f"Utilizador: {nome_do_novo_utilizador}")
print(f"Senha: {nova_senha}\n")
print("Copie a linha de hash abaixo (incluindo o b''):")
print(f"b'{novo_hash}'")
print("\n")