# main.py

import sys
import whois
import dns.resolver

def whois_lookup(domain):
    """
    Performs a WHOIS lookup for the given domain.
    """
    print(f"\n--- Recherche WHOIS pour {domain} ---")
    try:
        w = whois.whois(domain)
        print(w)
    except Exception as e:
        print(f"Erreur lors de la recherche WHOIS : {e}")

def dns_lookup(domain):
    """
    Performs DNS lookups (A, MX, TXT) for the given domain.
    """
    print(f"\n--- Recherche DNS pour {domain} ---")
    # Liste des types d'enregistrements à rechercher
    record_types = ['A', 'MX', 'TXT']
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            print(f"\nEnregistrements {record_type} :")
            for rdata in answers:
                print(f"  - {rdata.to_text()}")
        except dns.resolver.NoAnswer:
            print(f"  - Pas d'enregistrement {record_type} trouvé.")
        except Exception as e:
            print(f"  - Erreur lors de la recherche {record_type} : {e}")

def main():
    """
    Main function to run the OSINT tool.
    """
    # Vérifie si un nom de domaine est fourni en argument de ligne de commande
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        # Sinon, demande à l'utilisateur d'entrer un nom de domaine
        domain = input("Entrez le nom de domaine cible (ex: google.com) : ")

    if not domain:
        print("Aucun domaine n'a été fourni. Fermeture du programme.")
        return

    whois_lookup(domain)
    dns_lookup(domain)

# Point d'entrée du script
if __name__ == "__main__":
    main()