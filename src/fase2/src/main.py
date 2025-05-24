from subalgoritmos_main import *
import subalgoritmos_banco

def executar_codigo() -> None:
    def valida_campos(campos: list) -> bool:
        result = True

        print("\n")

        if campos[0] < 0 or campos[0] > 5:
            print("O produto deve ser um número de 1 a 5.")
            result = False

        if campos[1] < 0:
            print("A quantidade de produto armazenada em toneladas no silo deve ser maior ou igual a zero.")
            result = False

        if not campos[2]:
            print("O nome do silo não pode ser vazio.")
            result = False

        if not campos[3]:
            print("O endereço do silo não pode ser vazio.")
            result = False

        if campos[4] <= 0:
            print("A capacidade de armazenamento em toneladas do silo deve ser maior que zero.")
            result = False

        if campos[4] < campos[1]:
            print("A quantidade de produto armazenada no silo não pode ser maior do que a capacidade do próprio.")

        if not (0 <= campos[5] <= 100):
            print("A nível de umidade não pode ser maior que zero e nem maior que cem.")
            result = False

        if not (-10 <= campos[6] <= 50):
            print("A temperatura deve estar entre -10 graus célcius e 50 graus célcius.")
            result = False

        if not (0 <= campos[7] <= 14):
            print("O pH deve estar entre 0 e 14.")
            result = False
        return result

    limpar_console()

    executar = True

    print ("----->Sistema de Gerenciamento de Silos - Controle e Qualidade dos grãos armazenados<------\n")
    print ("Para começar, informe as credenciais de acesso ao banco de dados Oracle da FIAP, \nutilizado como DEFAULT na aplicação.\n")

    user = input("Usuário pessoal de acesso (RMXXXXXX) -> ")
    password = input("Senha de acesso -> ")

    while executar:
        subalgoritmos_banco.set_connection(user, password)
        subalgoritmos_banco.check_table_exists()
        if subalgoritmos_banco.conectado:
            print("")
            exibir_menu()
            try:
                escolha = input("Escolha -> ")
                escolha = int(escolha)
            except ValueError as e:
                print(f"{escolha} não é um valor inteiro!")
                continue
            except Exception as e:
                print(f"Ocorreu algum erro: {e}")
                continue

            limpar_console()

            def obter_dados_produto(tipo):
                match tipo:
                    case 1:
                        return subalgoritmos_banco.milho
                    case 2:
                        return subalgoritmos_banco.soja
                    case 3:
                        return subalgoritmos_banco.arroz
                    case 4:
                        return subalgoritmos_banco.trigo
                    case 5:
                        return subalgoritmos_banco.feijao
                    case _:
                        return None

            match escolha:
                case 1:
                    try:
                        while True:
                            nome_silo = input("Nome para este silo -> ")
                            capacidade = float(input("Capacidade máxima de armazenamento do silo (em toneladas) -> "))
                            exibir_tipo()
                            tipo = int(input("Código do produto armazenado -> "))
                            tipo_dados = obter_dados_produto(tipo)
                            quantidade = float(input("Quantidade armazenada deste produto (em toneladas) -> \n"))
                            endereco = input("Endereço em que se encontra o silo -> ")
                            print(f"\n-->Umidade dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[3]}% - {tipo_dados[4]}%)<--")
                            umidade = float(input("Nível atual de umidade dos grãos -> "))
                            print(f"\n-->Temperatura dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[5]}° C - {tipo_dados[6]}° C)<--")
                            temperatura = float(input("Temperatura atual dos grãos -> "))
                            print(f"\n-->pH dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[7]} - {tipo_dados[8]})<--")
                            pH = float(input("Informe o pH dos grãos -> "))
                            observacao = input("\nObservações -> ")
                            campos = [tipo, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, pH, observacao]
                            if valida_campos(campos):
                                break
                        if not observacao:
                            campos[8] = "Sem observações"
                        subalgoritmos_banco.insert(tipo, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, pH, observacao)
                    except ValueError as e:
                        print(f"Os campos numéricos devem ser preenchidos com números.")
                    except Exception as e:
                        print(f"Erro: {e}")

                case 2:
                    subalgoritmos_banco.get_id_nome()
                    while True:
                        id = input("Id -> ")
                        if id.isdigit():
                            id = int(id)
                            if id > 0:
                                break
                            else:
                                print("Selecione um valor inteiro maior que zero")
                        else:
                            print("Selecione um valor inteiro maior que zero")
                    subalgoritmos_banco.get(id)

                case 3:
                    subalgoritmos_banco.get_all()

                case 4:
                    try:
                        subalgoritmos_banco.get_id_nome()
                        while True:
                            while True:
                                id = int(input("\nId -> "))
                                if id > 0:
                                    break
                                else:
                                    print("Id deve ser maior que zero")
                            nome_silo = input("Nome para este silo -> ")
                            capacidade = float(input("Capacidade máxima de armazenamento do silo (em toneladas) -> "))
                            exibir_tipo()
                            tipo = int(input("Código do produto armazenado -> "))
                            tipo_dados = obter_dados_produto(tipo)
                            quantidade = float(input("Quantidade armazenada deste produto (em toneladas) -> \n"))
                            endereco = input("Endereço em que se encontra o silo -> ")
                            print(f"\n-->Umidade dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[3]}% - {tipo_dados[4]}%)<--")
                            umidade = float(input("Nível atual de umidade dos grãos -> "))
                            print(f"\n-->Temperatura dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[5]}° C - {tipo_dados[6]}° C)<--")
                            temperatura = float(input("Temperatura atual dos grãos -> "))
                            print(f"\n-->pH dos grãos (referência ideal para o {tipo_dados[1]}: {tipo_dados[7]} - {tipo_dados[8]})<--")
                            pH = float(input("Informe o pH dos grãos -> "))
                            observacao = input("\nObservações -> ")
                            campos = [tipo, quantidade, nome_silo, endereco, capacidade, umidade, temperatura, pH, observacao]
                            if valida_campos(campos):
                                break
                        if not observacao:
                            campos[8] = "Sem observações"
                        campos.insert(0, id)
                        subalgoritmos_banco.update(campos)
                    except ValueError as e:
                        print(f"Os campos numéricos devem ser preenchidos com números.")
                    except Exception as e:
                        print(f"Erro: {e}")

                case 5:
                    try:
                        subalgoritmos_banco.get_id_nome()
                        while True:
                            id = input("Id -> ")
                            if id.isdigit():
                                id = int(id)
                                if id > 0:
                                    break
                                else:
                                    print("Id deve ser um número inteiro e maior que zero")
                            else:
                                print("Id deve ser um número inteiro e maior que zero")
                        while True:
                            confirmacao = input("Confirmar exclusão: [S]im/[N]ão")
                            match confirmacao:
                                case "S" | "s":
                                    subalgoritmos_banco.delete(id)
                                    break
                                case "N" | "n":
                                    break
                                case _:
                                    print("Por favor, selecione uma opção válida")

                    except Exception as e:
                        print(f"Erro: {e}")

                case 6:
                    subalgoritmos_banco.gerar_relatorio()

                case 7:
                    subalgoritmos_banco.backup()

                case 8:
                    subalgoritmos_banco.restaurar_backup()

                case 9:
                    executar = False
                case _:
                    print(f"{escolha} não é uma opção válida, selecione outra opção.")
        else:
            while True:
                escolha = input("Conexão perdida, deseja tentar restabelecer conexão? [S]im/[N]ão\n")
                match escolha:
                    case "S" | "s":
                        user = input("Usuário do banco -> ")
                        password = input("Senha do banco -> ")
                        break
                    case "N" | "n":
                        executar = False
                        break
                    case _:
                        print("Opção inválida, por favor selecione outra")

    else:
        subalgoritmos_banco.close_connection()
        print("Obrigado por utilizar nosso programa!")

executar_codigo()
