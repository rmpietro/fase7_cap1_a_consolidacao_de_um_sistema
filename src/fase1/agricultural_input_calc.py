import pandas as pd

# Definindo os meses e os insumos principais
months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Quantidades estimadas de insumos (em gramas ou mililitros por metro quadrado, por mês, segundo pesquisa) dado o
# clima típico do estado de São Paulo
sugarcane_input = {
    "Nitrogênio": [5, 5, 5, 4, 3, 2, 0, 0, 1, 5, 6, 6],
    "Fósforo": [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    "Potássio": [3, 3, 3, 2, 2, 1, 0, 0, 1, 4, 5, 5],
    "Calcário": [0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0],
    "Micronutrientes": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
    "Herbicidas": [0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    "Inseticidas": [0, 0, 0, 0, 0.5, 0.5, 0, 0, 0, 0.5, 0.5, 0],
    "Bioestimulantes": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
}

corn_input = {
    "Nitrogênio": [4, 4, 5, 5, 3, 2, 1, 1, 0, 2, 4, 4],
    "Fósforo": [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    "Potássio": [2, 2, 3, 3, 2, 1, 0, 0, 1, 3, 4, 4],
    "Calcário": [0, 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0],
    "Micronutrientes": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
    "Herbicidas": [0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    "Inseticidas": [0, 0, 0, 0.5, 0.5, 0, 0, 0.5, 0, 0.5, 0.5, 0],
    "Bioestimulantes": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
}

# Criando DataFrames para organizar os dados a partir dos Dictionaries definidos para cada cultura
sugarcane_input_df = pd.DataFrame(sugarcane_input, index=months)
corn_input_df = pd.DataFrame(corn_input, index=months)

def calculate_input_consumption(crop_area, crop_type):
    if crop_type == "cana":
        # resultados sendo divididos por 1000 para converter de gramas para quilogramas
        input_consumption = sugarcane_input_df.mul(crop_area, axis=0).div(1000)
    elif crop_type == "milho":
        # resultados sendo divididos por 1000 para converter de gramas para quilogramas
        input_consumption = corn_input_df.mul(crop_area, axis=0).div(1000)
    else:
        raise print("Tipo de cultura inválido. Escolha 'cana (para cana-de-açúcar)' ou 'milho'.")

    return input_consumption