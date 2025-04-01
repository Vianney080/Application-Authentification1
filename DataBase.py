import sqlite3

def creer_base_de_donnees():
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            courriel TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            descripteur_facial TEXT
        )
    ''')
    connexion.commit()
    connexion.close()
    print("Base de données et table créées avec succès !")

#if __name__ == "__main__":
#creer_base_de_donnees() 