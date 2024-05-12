import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
from settings import key

def main():
    st.title('Welcome to Simple Shopping Mall')
    st.write('This is a simple shopping mall where you can buy a variety of products.')

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Login')
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            if st.button('Login'):
                response = requests.get('http://localhost:8000/login', params={"username": username, "password": password})
                if response.status_code == 200:
                    st.session_state.logged_in = True
                    st.session_state.user = response.json()["user"]
                    st.success(response.json()["message"])
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with col2:
            st.subheader('Sign Up')
            new_username = st.text_input('New Username')
            new_password = st.text_input('New Password', type='password')
            full_name = st.text_input('Full Name')
            address = st.text_input('Address')
            payment_info = st.text_input('Payment Info')
            if st.button('Sign Up'):
                response = requests.get('http://localhost:8000/register', params={"username": new_username, "password": new_password, "full_name": full_name, "address": address, "payment_info": payment_info})
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error("Failed to sign up.")

    if st.session_state.logged_in:
        if st.session_state.user["role"] == 'admin':
            st.sidebar.subheader('Admin Menu')
            menu = ['Home', 'Add Product', 'Purchase Management']
            choice = st.sidebar.selectbox('Menu', menu)

            if choice == 'Home':
                st.subheader('All Products')
                response = requests.get('http://localhost:8000/products')
                products = response.json()
                for product in products:
                    st.write(f"Name: {product['name']}, Category: {product['category']}, Price: ${product['price']}")
                    if 'thumbnail_url' in product and product['thumbnail_url'] != '':
                        st.image(product['thumbnail_url'], width=200)

            elif choice == 'Add Product':
                st.subheader('Add a New Product')
                with st.form(key='add_product_form'):
                    name = st.text_input('Product Name')
                    category = st.text_input('Category')
                    price = st.number_input('Price', min_value=0.0)
                    thumbnail_url = st.text_input('Thumbnail URL')
                    check_password = st.text_input('password')
                    submit_button = st.form_submit_button(label='Add')
                    
                    if submit_button:
                        add_product_response = requests.get('http://localhost:8000/add_product', params={"name": name, "category": category, "price": price, "thumbnail_url": thumbnail_url, "pw": check_password})
                        if add_product_response.status_code == 200:
                            st.success(add_product_response.json()["message"])
                        else:
                            st.error("Failed to add product.")

            # 구입목록 관리 페이지
            elif choice == 'Purchase Management':
                st.subheader('User Purchase Management')
                response = requests.get('http://localhost:8000/all_buy_list')
                products = response.json()
                
                df1 = pd.DataFrame(products)
                
                df1['Select'] = False
                df = st.data_editor(df1, disabled=["buy_id"], hide_index=True)

                selected_ids = []
                for index, row in df.iterrows():
                    if row['Select']:
                        selected_ids.append(row['buy_id'])

                delete_button = st.button(label='Del', type="primary")
                edite_button = st.button(label='Edit')
                
                if delete_button and len(selected_ids) > 0:
                    for del_item in selected_ids:
                        del_response = requests.get('http://localhost:8000/del_buy_list', params={"buy_id":del_item})
                        if del_response.status_code == 200:
                            st.success(del_response.json()["message"])
                        else:
                            st.error("Failed to del product.")
                    st.rerun()
                elif edite_button and len(selected_ids) > 0:
                    for del_item in selected_ids:
                        edit_item = df[df['buy_id']==del_item]
                        params = {
                            "buy_id": edit_item["buy_id"].values[0],
                            "uid": edit_item["uid"].values[0],
                            "pid": edit_item["pid"].values[0],
                            "date": edit_item["date"].values[0],
                            "state": edit_item["state"].values[0],
                            "u_address": edit_item["u_address"].values[0]
                        }
                        
                        edit_response = requests.get('http://localhost:8000/update_buy_list', params=params)
                        
                        if edit_response.status_code == 200:
                            st.success(edit_response.json()["message"])
                        else:
                            st.error("Failed to update")
                    st.rerun()


            if st.sidebar.button('Logout'):

                st.session_state.logged_in = False
                st.success('You have been logged out.')
                st.rerun()

        else:
            st.sidebar.subheader('User Menu')
            menu = ['Home', 'Buy Products', 'My Page']
            choice = st.sidebar.selectbox('Menu', menu)

            if choice == 'Home':
                st.subheader('All Products')
                response = requests.get('http://localhost:8000/products')
                products = response.json()
                for product in products:
                    st.write(f"Name: {product['name']}, Category: {product['category']}, Price: ${product['price']}")
                    if 'thumbnail_url' in product and product['thumbnail_url'] != '':
                        st.image(product['thumbnail_url'], width=200)

            elif choice == 'Buy Products':
                

                st.subheader('Buy Products')
                response = requests.get('http://localhost:8000/products')
                products = response.json()
                selected_product = st.selectbox('Select a product', [f"id: {product['id']}, name: {product['name']}, price:{product['price']}"  for product in products])
                user_address = st.text_input('Home Address')
                user_payment_info = st.text_input('Payment Info')
                product_id = int(selected_product[4:selected_product.find(",")])
                #product_price = selected_product[selected_product.index("price:") + len("price:"):]
                if st.button('Buy'):
                    tid = datetime.now().strftime("%Y%m%d%H%M%S")

                    # You can integrate with a payment gateway API here
                    url = 'https://kapi.kakao.com/v1/payment/ready'

                    secret_key = key
                    # 요청 헤더
                    headers = {
                        'Authorization': "KakaoAK " + secret_key,
                        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                    }
                    

                    # 결제 정보
                    params  = {
                        "cid": "TC0ONETIME", 
                        "partner_order_id": tid,  
                        "partner_user_id": "testuser",  
                        "item_name": selected_product, 
                        "quantity": 1, 
                        "total_amount": 1000 , 
                        "tax_free_amount": 0,  
                        "vat_amount" : 0,
                        "approval_url": f"http://localhost:8000/kakaopay/success?partner_order_id={tid}",
                        "fail_url": "http://localhost:8000/kakaopay/fail",
                        "cancel_url": "http://localhost:8000/kakaopay/cancel"
                    }
                    st.write(params)
                    # 요청 보내기
                    response = requests.post(url, headers=headers, params=params )
                    tid = response.json()['tid']
                    save_tid = requests.get('http://localhost:8000/add_tid', params={"buy_id":tid, "tid":tid})
                    # 응답 확인
                    st.error(response.status_code)
                    st.error(response.text)
                    if response.status_code == 200:
                        st.success("결제 요청이 성공적으로 완료되었습니다.")
                        payment_url = response.json().get("next_redirect_pc_url")
                        st.link_button("kakaopay", payment_url)
                        add_buy_response = requests.get('http://localhost:8000/add_buy', params={"user_id": st.session_state.user["id"], "product_id": int(selected_product[4:selected_product.find(',')]), "state": True, "address": user_address})

                    elif response.status_code == 400:
                        st.error("결제 요청에 실패했습니다.")
                    else:
                        st.error("결제 요청을 취소하셨습니다.")

            elif choice == 'My Page':
                st.subheader('My Page')
                st.write(f'Username: {st.session_state.user["username"]}')
                st.write(f'Full Name: {st.session_state.user["full_name"]}')
                st.write(f'Address: {st.session_state.user["address"]}')
                st.write(f'Payment Info: {st.session_state.user["payment_info"]}')
                
                with st.form(key='edit_user_info_form'):
                    new_full_name = st.text_input('Full Name', value=st.session_state.user["full_name"])
                    new_address = st.text_input('Address', value=st.session_state.user["address"])
                    new_payment_info = st.text_input('Payment Info', value=st.session_state.user["payment_info"])
                    update_check_password = st.text_input('password')
                    submit_button = st.form_submit_button(label='Update Info')

                    if submit_button:
                        response = requests.get('http://localhost:8000/update_user_info', params={"id":st.session_state.user["id"], "full_name": new_full_name, "address": new_address, "payment_info": new_payment_info, "pw": update_check_password})
                        if response.status_code == 200:
                            st.success('User information updated successfully!')
                            st.session_state.user["full_name"] = new_full_name
                            st.session_state.user["address"] = new_address
                            st.session_state.user["payment_info"] = new_payment_info
                            st.rerun()
                        else:
                            st.error("Failed to update user information.")
                # 사용자 구매 목록 페이지
                st.subheader('my buy list')
                response = requests.get('http://localhost:8000/user_buy_list', params={"user_id": st.session_state.user["id"]})
                user_buy_list = response.json()
                for item in user_buy_list:
                    st.write(f"Product ID: {item['pid']}, DATE: {item['date']}, STATE: {item['state']}, ADDRESS: {item['u_address']}")

                if st.button('Logout', key='logout_btn'): # 에러 수정을 위해 key 추가
                    st.session_state.logged_in = False
                    st.success('You have been logged out.')
                    st.rerun()

            
            if st.sidebar.button('Logout'):
                st.session_state.logged_in = False
                st.success('You have been logged out.')
                st.rerun()

if __name__ == '__main__':
    main()
