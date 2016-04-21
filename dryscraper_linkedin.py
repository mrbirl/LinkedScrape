from datetime import datetime
import json
import time
import sys
from bs4 import BeautifulSoup
import dryscrape


class LinkScrape:

    LOGIN_EMAIL = 'EMAIL'
    LOGIN_PASSWORD = 'PASSWORD'
    BASE_URL = 'https://www.linkedin.com'
    sess = None
    RESULTS = {}

    def __init__(self, email, password, loadprevious):
        try:
            self.load_results()
        except:
            print 'No past results loaded'
        self.LOGIN_EMAIL = email
        self.LOGIN_PASSWORD = password
        # set up a web scraping session
        self.sess = dryscrape.Session(base_url=self.BASE_URL)
        # we don't need images
        self.sess.set_attribute('auto_load_images', False)
        # visit homepage and log in
        self.login()
        if not loadprevious:
            urls = self.get_all_linkedin_company_urls()
        else:
            urls = self.load_companies()
        self.process_companies(urls)

    def find_employee_blanks(self):
        failed_companies = self.load_failed_companies()
        for company_name, company_insights in self.RESULTS.iteritems():
            employees = company_insights['employees']
            if not employees:
                failed_companies[company_name] = company_insights['linkedin']
                self.save_failed_companies(failed_companies)

    def get_all_linkedin_company_urls(self):
        '''
            Iterates through every page in the search results
            and builds list of company names & LinkedIn URLS.

            Returns:
                dict: Company names mapped to LinkedIn URLs
        '''
        company_links = {}

        # Search for 51-200 employee companies in Retail, Apparel & Fashion,
        # in Ireland, USA, UK, Canada
        # int_fashion_retail = 'https://www.linkedin.com/vsearch/c?type=companies&orig=\
        #                       FCTD&rsid=1219664211436979526645&pageKey=oz-winner&searc\
        #                       h=Search&f_CCR=us%3A0,gb%3A0,ie%3A0,ca%3A0&f_I=27,19&open\
        #                       Facets=N,CCR,JO,I,CS&f_CS=D'

        # Hospitality sector companies in Ireland, with 51-5000 employees
        irl_hospitality = 'https://www.linkedin.com/vsearch/c?type=companies&orig\
                           =FCTD&rsid=1219664211455638914865&pageKey=oz-winner&sea\
                           rc\%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%2\
                           0%20%20%20%20%20%20%20h=Search&f_CCR=ie%3A0&open\%20%20%2\
                           0%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%2\
                           0%20%20%20Facets=N,CCR,JO,I,CS&openFacets=N,CCR,JO,I,CS&\
                           f_I=31&f_CS=D,E,F,G'

        self.sess.visit(irl_hospitality)

        # Iterate over search results pages
        while 1:
            # Get HTML for this page & extract links
            html = self.sess.body()
            soup = BeautifulSoup(html, 'lxml')
            for i in range(1, 10):
                try:
                    result = soup.find("li", {"class": "mod result \
                                            idx{num} company".format(num=i)})
                    anchor = result.find("a", {"class": "title"})
                    link = self.BASE_URL + anchor.get('href')
                    name = anchor.contents[0]
                    print 'Added LinkedIn URL for {name}'.format(name=name)
                    company_links[name] = link
                    self.save_company_links(company_links)
                except Exception as e:
                    print e
            # Get the URL of the next search page, if it exists
            next_page_url = soup.find("a", {
                                "class": "page-link",
                                "title": "Next Page"})
            if next_page_url:
                time.sleep(1)
                next_page_url = self.BASE_URL + next_page_url.get('href')
                self.sess.visit(next_page_url)
            else:
                return company_links

    def get_employees(self, soup):
        '''
            Checks each company employee to find marketing people.

            Args:
                (str) soup: BeautifulSoup object for company page

            Returns:
                dict: Marketing employees and their details
        '''
        employee_details = {}
        # Get search results for employees in this company
        employees_box = soup.find("div", {"class": "company-density module"})
        view_all_link = employees_box.find("a", {"class": "more"}).get("href")
        view_all_link = self.BASE_URL + view_all_link
        self.sess.visit(view_all_link)
        # Iterate over all the employees
        while 1:
            time.sleep(3)
            html = self.sess.body()
            soup = BeautifulSoup(html, 'lxml')
            for i in range(1, 10):
                self.sess.render('employeePage.png')
                try:
                    result = soup.find("li", {"class": "mod result \
                                        idx{num} people".format(num=i)})
                    if result:  # Otherwise no more result items
                        anchor = result.find("a", {"class": "title"})
                        link = anchor.get('href')
                        name = anchor.text
                        description = result.find("div", {"class":
                                                          "description"}).text
                        if ('marketing' in description.lower() or
                                'cmo' in description.lower()):
                            employee_details[name] = {
                                'link': link,
                                'description': description
                            }
                            print 'Found marketeer: {name}'.format(name=name)
                except Exception as e:
                    print e
            # Get the URL of the next search page, if it exists
            next_page_url = soup.find("a", {
                                "class": "page-link",
                                "title": "Next Page"})
            if next_page_url:
                next_page_url = self.BASE_URL + next_page_url.get('href')
                self.sess.visit(next_page_url)
            else:
                return employee_details

    def process_companies(self, linkedin_urls):
        '''
            Given company linkedin URL, get company & employee details
            Iterates thorugh RESULTS and adds new info.
        '''
        try:
            failed_companies = self.load_failed_companies()
        except:
            failed_companies = {}  # When can't get details automatically

        for company_name, linkedin_url in linkedin_urls.iteritems():
            if (company_name not in self.RESULTS or
                    company_name in failed_companies):
                self.sess.visit(linkedin_url)  # Visit linkedin page
                self.sess.render('companyPage.png')
                html = self.sess.body()
                soup = BeautifulSoup(html, 'lxml')
                try:
                    # Get list item containing website
                    website = soup.find("li", {"class": "website"})
                    website = website.find("a").text
                    print website
                    # Get Industry
                    industry = soup.find("li", {"class": "industry"})
                    industry = industry.find("p").text
                    print industry
                    # Get Size
                    size = soup.findAll("a", {"class": "density"})
                    try:
                        size = size[1].text
                    except:
                        size = size[0].text
                    print size
                    if 25 <= int(size.replace(',', '')) <= 250:
                        ts = time.time()
                        ts = datetime.fromtimestamp(
                             ts).strftime('%Y-%m-%d %H:%M:%S')
                        print ts
                        employees = self.get_employees(soup)
                        if employees:
                            company_insights = {
                                'linkedin': linkedin_url,
                                'website': website,
                                'industry': industry,
                                'size': size,
                                'employees': employees,
                                'processed': ts
                            }
                            print 'Processed {name}:'.format(name=company_name)
                            print company_insights
                            self.RESULTS[company_name] = company_insights
                            self.save_results()
                        else:
                            failed_companies[company_name] = linkedin_url
                            self.save_failed_companies(failed_companies)
                except Exception as e:
                    print e
                    failed_companies[company_name] = linkedin_url
                    self.save_failed_companies(failed_companies)
                    print 'Cant get details for company: \
                           {url}'.format(url=linkedin_url)
                time.sleep(3)
            else:
                print 'Company already processed: {}'.format(company_name)

    def login(self):
        '''
            Assumes user is not signed in - signs them in
        '''
        print 'Logging in...'
        self.sess.visit('/')
        html = self.sess.body()
        soup = BeautifulSoup(html, 'lxml')
        email_field = self.sess.at_css('#login-email')
        password_field = self.sess.at_css('#login-password')
        email_field.set(self.LOGIN_EMAIL)
        password_field.set(self.LOGIN_PASSWORD)
        # signin = self.sess.at_css('#signin')
        signin = soup.find("input", {"value": "Sign in"})
        print signin
        time.sleep(1)  # Give the signin button a second to become active
        self.sess.render('loginPage.png')
        signin.click()
        print 'Logged In'

    def load_companies(self):
        '''
            Company links from Json
        '''
        with open('company_links.json', 'r') as links_file:
            links = json.load(links_file)
        print 'Loaded company links.'
        return links

    def load_results(self):
        '''
            Results from Json
        '''
        with open('results.json', 'r') as results_file:
            self.RESULTS = json.load(results_file)
        print 'Loaded past results.'

    def load_failed_companies(self):
        '''
            Failed from Json

            Returns:
                dict: Company name mapped to LinkedIn url
        '''
        with open('failed_links.json', 'r') as failed_file:
            failed_companies = json.load(failed_file)
        print 'Loaded past results.'
        return failed_companies

    def save_company_links(self, links):
        '''
            Company links to Json, in case of crash
        '''
        with open('company_links.json', 'w+') as links_file:
            json.dump(links, links_file)
        print 'Saved company links.'

    def save_failed_companies(self, failed_companies):
        '''
            Failed company links to Json, for manual review
        '''
        with open('failed_links.json', 'w+') as failed_file:
            json.dump(failed_companies, failed_file)
        print 'Saved failed company links.'

    def save_results(self):
        '''
            RESULTS to Json file
        '''
        with open('results.json', 'w+') as results_file:
            json.dump(self.RESULTS, results_file)
        print 'Saved Results'

email = str(sys.argv[1])
password = str(sys.argv[2])
try:
    load_previous = str(sys.argv[3])
except:
    load_previous = False
scraper = LinkScrape(email, password, load_previous)
