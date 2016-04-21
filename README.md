# LinkedScrape
A personal project to automatically navigate LinkedIn and find profiles that match search criteria.

First searches for a specific type of company - e.g. tech companies in the US with more than 500 employees. Then looks for a specific type of person in those companies - e.g. someone in a marketing role. 

Gathers these company details:
* LinkedIn URL
* Website
* Industry
* Size

and these details on each employee fitting the search criteria:
* Name
* LinkedIn URL
* Description

Use <i>json_to_spreadsheet.py</i> to write everythig to a spreadsheet.

There's a limit to the amount of searches you can do each day on LinkedIn, so you can optionally load previous results when running the script, to continue on from last time.

## Setup

Needs a LinkedIn account to use for search and scrape.
Run with:

```shell
python dryscrape_linkedin.py linkedin_email linkedin_password
```

To load previous results and continue from there (to avoid finding the same people and companies again):

```shell
python dryscrape_linkedin.py linkedin_email linkedin_password true
```

where <i>linkedin_email</i> is the email address you use to sign in to LinkedIn, and <i>linkedin_password</i> is your password.


## Login Issues
LinkedIn's signin page seems to change a lot, so you'll likely have to the login() in dryscrape.py if signin isn't working. Usually requires looking at these two lines:

```python
email_field = self.sess.at_css('#login-email')
password_field = self.sess.at_css('#login-password')
```
and this

```python
signin = soup.find("input", {"value": "Sign in"})
```

in particular.

## Finding specific company types

The search terms for finding companies can be updated. First copy one of the search query URL's in dryscrape_linkedin.py to your browser first. A query like this:

<i>https://www.linkedin.com/vsearch/c?type=companies&orig=FCTD&rsid=1219664211436979526645&pageKey=oz-winner&search=Search&f_CCR=us%3A0,gb%3A0,ie%3A0,ca%3A0&f_I=27,19&openFacets=N,CCR,JO,I,CS&f_CS=D</i>

should give you access to the full advanced LinkedIn search, without having a premium account. Set the search criteria you want from the menu on the left, then copy the new URL back to 

```python
def get_all_linkedin_company_urls
```

## Finding specific job types
You can specify the type of people you're looking for. Right now it's searching for marketing people (someone with marketing or CMO in their profile description. In

```python 
def get_employees()
```

look for 

```python
if ('marketing' in description.lower() or
	'cmo' in description.lower()):
```
and replace those criteria with whatever you want.

## Disclaimer
###### Automated scraping of LinkedIn is usually against LinkedIn T's & C's. This is a personal experimentation project only, use at your own risk etc. :)