import navigation as nav
import uuid
import random as rd
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta,date


fake = Faker(locale='pt-BR')

# Cost categories (be my guest and expand this list at will)
cost_categories1 = [
    "ALUGUEL", 
    "SALARIOS", 
    "UTILIDADES", 
    "MARKETING", 
    "INVENTARIO", 
    "MANUTENCAO", 
    "SEGURANCA", 
    "SEGUROS"
]


dim_municipio = pd.read_sql(nav.read_sql_file('person'), nav.sqlite_conn)

# Generate Fake Data
def generate_center_cost_data(num_centers=10):
    centers = []
    
    for _ in range(num_centers):
        dd = date(2023,1,1)
        index = rd.choice(range(len(dim_municipio)))
        center_id = str(uuid.uuid4())
        parent_center_id = str(uuid.uuid4()) if rd.random() < 0.2 else None  # 20% chance of having a parent
        region = dim_municipio['nome_mesorregiao'].iloc[index]
        state = dim_municipio['nome_uf'].iloc[index]
        city = dim_municipio['nome_municipio'].iloc[index]
        address = fake.address()
        store_type = rd.choice(['Bovinos', 'Caprinos', 'Ovinos', 'Avinos', 'Grãos'])
        opening_date = fake.date_between(start_date="-5y", end_date=dd)
        status = rd.choice(["Ativo", "Encerrado", "Em renovação"])
        manager_id = str(uuid.uuid4())
        currency = "BRL"
        
        # Financials
        budget_allocated = round(rd.uniform(50000, 500000), 2)  # Between 50k and 500k
        actual_expenditure = round(budget_allocated * rd.uniform(0.7, 1.3), 2)  # 70-130% of budget
        actual_revenue = round(actual_expenditure * rd.uniform(1.1, 2.5), 2)  # 110-250% of expenditure
        profit_margin = round((actual_revenue - actual_expenditure) / actual_revenue, 2)

        # Generate Cost Categories Breakdown
        cost_categories2 = []
        total_spent = 0
        while len(cost_categories2) < 4:
            category_budget = round(budget_allocated * rd.uniform(0.05, 0.3), 2)
            category_spent = round(category_budget * rd.uniform(0.8, 1.2), 2)
            cost_categories2.append({
                "id_categoria": str(uuid.uuid4()),
                "nome_categoria": rd.choice(cost_categories1),
                "orcamento_disponivel": category_budget,
                "despesas_realizadas": category_spent
            })

        centers.append({
            "cod_centro_de_custo": center_id,
            "nome_centro_de_custo": f"Centro {fake.company()}",
            "ccusto_superior": parent_center_id,
            "regiao": region,
            "estado": state,
            "cidade": city,
            "endereço": address,
            "tipo_setor": store_type,
            "data_abertura": opening_date.strftime("%Y-%m-%d"),
            "status": status,
            "id_gerente": manager_id,
            "moeda": currency,
            "alocação_orcamento": budget_allocated,
            "despesas": actual_expenditure,
            "realizado_receitas": actual_revenue,
            "marge_lucro": profit_margin,
            "categoria_id": cost_categories2[0]["id_categoria"],
            "categoria_nome": cost_categories2[0]["nome_categoria"],
            "categoria_orcamento": cost_categories2[0]["orcamento_disponivel"],
            "categoria_despesa": cost_categories2[0]["despesas_realizadas"],
            "data_criação": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ultima_atualização": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return centers
# Generate 20 fake cost centers
# cost_centers_data = generate_center_cost_data(20)

# Convert to DataFrame and Export
# df = pd.DataFrame(cost_centers_data)
# df.to_json("dim_center_cost.json", orient="records", indent=4)

print("Success!")


# # 

# {
#   "center_id": "UUID",
#   "center_name": "string",
#   "parent_center_id": "UUID",
#   "region": "string",
#   "state": "string",
#   "city": "string",
#   "address": "string",
#   "store_type": "string",
#   "opening_date": "YYYY-MM-DD",
#   "status": "string",
#   "manager_id": "UUID",
#   "currency": "string",
#   "budget_allocated": "decimal",
#   "actual_expenditure": "decimal",
#   "actual_revenue": "decimal",
#   "profit_margin": "decimal",
#   "cost_categories": [
#     {
#       "category_id": "UUID",
#       "category_name": "string",
#       "allocated_budget": "decimal",
#       "actual_spent": "decimal"
#     }
#   ],
#   "created_at": "YYYY-MM-DD HH:MM:SS",
#   "updated_at": "YYYY-MM-DD HH:MM:SS"
# }
