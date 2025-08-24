from flask import Flask, render_template, request, jsonify, make_response
from jinja2 import FileSystemLoader, Environment
from weasyprint import HTML
import whois
import dns.resolver
import json

# Vos fonctions whois_lookup et dns_lookup restent les mêmes.
def whois_lookup(domain):
    output = f"\n--- Recherche WHOIS pour {domain} ---\n"
    try:
        w = whois.whois(domain)
        output += str(w)
    except Exception as e:
        output += f"Erreur lors de la recherche WHOIS : {e}"
    return output

def dns_lookup(domain):
    output = f"\n--- Recherche DNS pour {domain} ---\n"
    record_types = ['A', 'MX', 'TXT']
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            output += f"\nEnregistrements {record_type} :\n"
            for rdata in answers:
                output += f"  - {rdata.to_text()}\n"
        except dns.resolver.NoAnswer:
            output += f"  - Pas d'enregistrement {record_type} trouvé.\n"
        except Exception as e:
            output += f"  - Erreur lors de la recherche {record_type} : {e}\n"
    return output
    
def extract_summary(full_results):
    try:
        whois_data = whois.whois(full_results['domain'])
        whois_summary = f"Création: {whois_data.creation_date}\n" \
                        f"Expiration: {whois_data.expiration_date}\n" \
                        f"Serveurs de noms: {whois_data.name_servers}"
    except Exception as e:
        whois_summary = f"Erreur lors de la recherche WHOIS pour le résumé : {e}"

    dns_summary = ""
    try:
        a_records = dns.resolver.resolve(full_results['domain'], 'A')
        dns_summary += "Adresses IP (A Records):\n"
        for rdata in a_records:
            dns_summary += f"- {rdata.to_text()}\n"
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        dns_summary += "Pas d'adresse IP trouvée.\n"
    except Exception as e:
        dns_summary += f"Erreur lors de la recherche DNS pour le résumé : {e}\n"
    
    return whois_summary, dns_summary

app = Flask(__name__)

# Configuration Jinja2 mise à jour
template_paths = [
    './templates',
    './pdf_templates'
]
app.jinja_env.loader = FileSystemLoader(template_paths)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    domain = request.json['domain']
    if not domain:
        return jsonify({'results': 'Veuillez entrer un nom de domaine.'})

    whois_results = whois_lookup(domain)
    dns_results = dns_lookup(domain)
    full_results_text = whois_results + "\n\n" + dns_results

    try:
        whois_data = whois.whois(domain)
        # Création du résumé Whois complet et uniformisé
        whois_summary_text = f"Création: {whois_data.creation_date}\n" \
                             f"Expiration: {whois_data.expiration_date}\n" \
                             f"Serveurs de noms: {', '.join(whois_data.name_servers) if whois_data.name_servers else 'N/A'}\n" \
                             f"ID du domaine: {whois_data.domain_id if hasattr(whois_data, 'domain_id') and whois_data.domain_id else 'N/A'}\n" \
                             f"Nom du domaine: {whois_data.domain_name if hasattr(whois_data, 'domain_name') and whois_data.domain_name else 'N/A'}\n" \
                             f"Date de mise à jour: {whois_data.updated_date if hasattr(whois_data, 'updated_date') and whois_data.updated_date else 'N/A'}\n" \
                             f"Registrar: {whois_data.registrar if hasattr(whois_data, 'registrar') and whois_data.registrar else 'N/A'}"
    except Exception:
        whois_summary_text = "Impossible d'extraire le résumé WHOIS."
        
    dns_summary = ""
    try:
        a_records = dns.resolver.resolve(domain, 'A')
        dns_summary += "Adresses IP (A Records):\n"
        for rdata in a_records:
            dns_summary += f"- {rdata.to_text()}\n"
    except Exception:
        dns_summary += "Pas d'adresse IP trouvée."

    return jsonify({
        'full_results': full_results_text,
        # Envoi d'une seule variable pour le résumé Whois
        'whois_summary': whois_summary_text, 
        'dns_summary': dns_summary,
        'domain': domain
    })

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    report_type = data['type']
    domain = data['domain']
    
    if report_type == 'summary':
        # On récupère le résumé Whois complet
        whois_summary = data['whois_summary']
        dns_summary = data['dns_summary']
        
        rendered_html = render_template('summary_report.html', 
                                        title=f"Résumé pour {domain}", 
                                        domain=domain, 
                                        whois_summary=whois_summary, 
                                        dns_summary=dns_summary)
    elif report_type == 'full':
        full_results = data['full_results']
        rendered_html = render_template('full_report.html', 
                                        title=f"Rapport Complet pour {domain}", 
                                        domain=domain, 
                                        results=full_results)
    else:
        return jsonify({'error': 'Type de rapport non valide.'}), 400

    pdf = HTML(string=rendered_html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={domain}_{report_type}_report.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)