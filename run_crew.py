from app_main import CompanyBlogOrchestrator

def main():
    company_name = input("Company Name: ")
    company_website = input("Company Website: ")
    orchestrator = CompanyBlogOrchestrator(company_name, company_website)
    orchestrator.run()

if __name__ == "__main__":
    main()