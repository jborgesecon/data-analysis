# This code was 100% made by DeepThink under the prompt (give me a full ERP in streamlit for my bakery)
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state for data storage
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['ItemID', 'Ingredient', 'Quantity', 'Unit', 'Reorder_Level'])
if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=['OrderID', 'Customer', 'Items', 'Quantity', 'Total', 'Status', 'Date'])
if 'production' not in st.session_state:
    st.session_state.production = pd.DataFrame(columns=['BatchID', 'Product', 'Quantity', 'Production_Date', 'Status'])
if 'recipes' not in st.session_state:
    st.session_state.recipes = pd.DataFrame(columns=['RecipeID', 'Product', 'Ingredients', 'Quantities'])
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=['CustomerID', 'Name', 'Phone', 'Email', 'Loyalty_Points'])

def main():
    st.title("🍞 Bakery ERP System")
    
    menu = ["Dashboard", "Inventory Management", "Sales Tracking", 
            "Production Planning", "Recipes Management", "Customer Management"]
    choice = st.sidebar.selectbox("Navigation", menu)
    
    if choice == "Dashboard":
        show_dashboard()
    elif choice == "Inventory Management":
        inventory_management()
    elif choice == "Sales Tracking":
        sales_tracking()
    elif choice == "Production Planning":
        production_planning()
    elif choice == "Recipes Management":
        recipe_management()
    elif choice == "Customer Management":
        customer_management()

def show_dashboard():
    st.header("Bakery Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Inventory Items", len(st.session_state.inventory))
    with col2:
        st.metric("Pending Orders", len(st.session_state.orders[st.session_state.orders['Status'] == 'Pending']))
    with col3:
        st.metric("Production Today", len(st.session_state.production[
            st.session_state.production['Production_Date'] == datetime.today().strftime('%Y-%m-%d')
        ]))
    
    st.subheader("Recent Orders")
    st.dataframe(st.session_state.orders.tail(5))
    
    st.subheader("Low Stock Alerts")
    low_stock = st.session_state.inventory[st.session_state.inventory['Quantity'] < st.session_state.inventory['Reorder_Level']]
    st.dataframe(low_stock)

def inventory_management():
    st.header("Inventory Management")
    
    with st.expander("Add New Ingredient"):
        with st.form("inventory_form"):
            col1, col2 = st.columns(2)
            with col1:
                ingredient = st.text_input("Ingredient Name")
                quantity = st.number_input("Quantity", min_value=0.0)
            with col2:
                unit = st.selectbox("Unit", ["kg", "g", "L", "ml", "units"])
                reorder = st.number_input("Reorder Level", min_value=0.0)
            
            if st.form_submit_button("Add Ingredient"):
                new_item = pd.DataFrame([[len(st.session_state.inventory)+1, ingredient, quantity, unit, reorder]],
                                       columns=['ItemID', 'Ingredient', 'Quantity', 'Unit', 'Reorder_Level'])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_item])
                st.success("Ingredient added!")
    
    st.subheader("Current Inventory")
    st.dataframe(st.session_state.inventory)
    
    with st.expander("Update Inventory"):
        selected_item = st.selectbox("Select Ingredient", st.session_state.inventory['Ingredient'])
        new_quantity = st.number_input("New Quantity", min_value=0.0)
        if st.button("Update Stock"):
            index = st.session_state.inventory.index[st.session_state.inventory['Ingredient'] == selected_item].tolist()[0]
            st.session_state.inventory.at[index, 'Quantity'] = new_quantity
            st.success("Stock updated!")

def sales_tracking():
    st.header("Sales Tracking")
    
    with st.expander("Create New Order"):
        with st.form("order_form"):
            customer = st.text_input("Customer Name")
            items = st.multiselect("Select Items", get_available_products())
            quantities = st.number_input("Quantity", min_value=1)
            
            if st.form_submit_button("Create Order"):
                total = calculate_order_total(items, quantities)
                new_order = pd.DataFrame([[
                    len(st.session_state.orders)+1,
                    customer,
                    ", ".join(items),
                    quantities,
                    total,
                    "Pending",
                    datetime.today().strftime('%Y-%m-%d')
                ]], columns=['OrderID', 'Customer', 'Items', 'Quantity', 'Total', 'Status', 'Date'])
                st.session_state.orders = pd.concat([st.session_state.orders, new_order])
                st.success("Order created!")
    
    st.subheader("Recent Orders")
    st.dataframe(st.session_state.orders)
    
    with st.expander("Update Order Status"):
        order_id = st.number_input("Order ID", min_value=1, max_value=len(st.session_state.orders))
        new_status = st.selectbox("New Status", ["Pending", "Processing", "Completed"])
        if st.button("Update Status"):
            st.session_state.orders.at[order_id-1, 'Status'] = new_status
            st.success("Status updated!")

def get_available_recipes():
    if not st.session_state.recipes.empty:
        return st.session_state.recipes['Product'].unique().tolist()
    return []

def production_planning():
    st.header("Production Planning")
    
    with st.expander("Create Production Batch"):
        with st.form("production_form"):
            product = st.selectbox("Select Product", get_available_recipes())
            quantity = st.number_input("Batch Quantity", min_value=1)
            production_date = st.date_input("Production Date")
            
            if st.form_submit_button("Schedule Production"):
                if check_ingredients_availability(product, quantity):
                    update_inventory_for_production(product, quantity)
                    new_batch = pd.DataFrame([[
                        len(st.session_state.production)+1,
                        product,
                        quantity,
                        production_date.strftime('%Y-%m-%d'),
                        "Scheduled"
                    ]], columns=['BatchID', 'Product', 'Quantity', 'Production_Date', 'Status'])
                    st.session_state.production = pd.concat([st.session_state.production, new_batch])
                    st.success("Production batch created!")
                else:
                    st.error("Not enough ingredients available!")
    
    st.subheader("Production Schedule")
    st.dataframe(st.session_state.production)

def recipe_management():
    st.header("Recipe Management")
    
    with st.expander("Add New Recipe"):
        with st.form("recipe_form"):
            product = st.text_input("Product Name")
            ingredients = st.multiselect("Select Ingredients", st.session_state.inventory['Ingredient'])
            quantities = st.number_input("Quantity Needed", min_value=0.1)
            
            if st.form_submit_button("Add Recipe"):
                new_recipe = pd.DataFrame([[
                    len(st.session_state.recipes)+1,
                    product,
                    ", ".join(ingredients),
                    quantities
                ]], columns=['RecipeID', 'Product', 'Ingredients', 'Quantities'])
                st.session_state.recipes = pd.concat([st.session_state.recipes, new_recipe])
                st.success("Recipe added!")
    
    st.subheader("Current Recipes")
    st.dataframe(st.session_state.recipes)

def customer_management():
    st.header("Customer Management")
    
    with st.expander("Add New Customer"):
        with st.form("customer_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email")
            
            if st.form_submit_button("Add Customer"):
                new_customer = pd.DataFrame([[
                    len(st.session_state.customers)+1,
                    name,
                    phone,
                    email,
                    0
                ]], columns=['CustomerID', 'Name', 'Phone', 'Email', 'Loyalty_Points'])
                st.session_state.customers = pd.concat([st.session_state.customers, new_customer])
                st.success("Customer added!")
    
    st.subheader("Customer List")
    st.dataframe(st.session_state.customers)

# Helper functions
def get_available_products():
    return st.session_state.recipes['Product'].tolist()

def calculate_order_total(items, quantities):
    # Simplified calculation - implement actual pricing logic
    return len(items) * quantities * 5.99

def check_ingredients_availability(product, quantity):
    recipe = st.session_state.recipes[st.session_state.recipes['Product'] == product].iloc[0]
    required_ingredients = recipe['Ingredients'].split(", ")
    required_quantities = recipe['Quantities'] * quantity
    
    for ing in required_ingredients:
        inventory_item = st.session_state.inventory[st.session_state.inventory['Ingredient'] == ing]
        if inventory_item.empty or inventory_item['Quantity'].values[0] < required_quantities:
            return False
    return True

def update_inventory_for_production(product, quantity):
    recipe = st.session_state.recipes[st.session_state.recipes['Product'] == product].iloc[0]
    required_ingredients = recipe['Ingredients'].split(", ")
    required_quantities = recipe['Quantities'] * quantity
    
    for ing in required_ingredients:
        index = st.session_state.inventory.index[st.session_state.inventory['Ingredient'] == ing].tolist()[0]
        current_qty = st.session_state.inventory.at[index, 'Quantity']
        st.session_state.inventory.at[index, 'Quantity'] = current_qty - required_quantities

if __name__ == "__main__":
    main()