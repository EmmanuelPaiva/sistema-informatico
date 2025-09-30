from argon2 import PasswordHasher

ph = PasswordHasher()

usuario = "admin2"
password = "48884368"

# Generar hash Argon2id
hash_pass = ph.hash(password)

print("Usuario:", usuario)
print("Hash Argon2id:")
print(hash_pass)
