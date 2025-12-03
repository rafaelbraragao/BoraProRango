import os

def menu():
    while True:
        print("\n=== MENU DE TESTES ===")
        print("[1] Testar geração e validação de token")
        print("[2] Testar pagamento PIX com Mercado Pago")
        print("[3] Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            os.system("python test_token.py")
        elif escolha == "2":
            os.system("python teste_pix.py")
        elif escolha == "3":
            print("Encerrando o menu. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()