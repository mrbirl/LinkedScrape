# LinkedScrape
A personal project to automatically navigate LinkedIn and find profiles that match search criteria.

Needs a LinkedIn account to use for search and scrape.
Run with:
python dryscrape_linkedin.py linkedin_email linkedin_password

LinkedIn's signin page seems to change a lot, so you'll likely have to the login() in dryscrape.py if signin isn't working. Usually requires looking at these two lines:

```python
email_field = self.sess.at_css('#login-email')
password_field = self.sess.at_css('#login-password')
```

in particular.

###### Automated scraping of LinkedIn is usually against LinkedIn T's & C's. This is a personal experimentation project only, use at your own risk etc. :)