# ERC-4337 UserOperations Indexer 🚀

Interface web permettant d'explorer et filtrer les transactions ERC-4337 (UserOperations) sur la blockchain avec stockage PostgreSQL.

1. **Prérequis**
   - Python 3.8+
   - PostgreSQL
   - Un RPC Ethereum (Infura, Alchemy...)
  
2. **Installation**
git clone https://github.com/votre-username/erc4337-indexer.git
cd erc4337-indexer
pip install -r requirements.txt

3. **Configuration**
cp .env.example .env

Remplir `.env` avec :
DB_HOST=localhost
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
RPC_URL=your_rpc_url

4. **Base de données**
createdb your_database # Créer la base PostgreSQL
python init_db.py # Initialiser les tables

5. **Lancer**
python app.py
Ouvrir `http://localhost:3000` 🌐

![image](https://github.com/user-attachments/assets/01704550-4c5f-4fcf-ac5c-9c93c4615077)
