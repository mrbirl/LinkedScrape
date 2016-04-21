import json
import bitly_api
import xlsxwriter


'''
Takes results from dyscrape_linkedin.py, writes them to a
spreadsheet.
'''

# Load results
results = {}
with open('results.json', 'r') as results_file:
    results = json.load(results_file)
print 'Loaded past results.'


# Define your API information


TOKEN = "YOUR_BITLY_TOKEN"  # See http://dev.bitly.com

bt_conn = bitly_api.Connection(access_token=TOKEN)

workbook = xlsxwriter.Workbook('results.xlsx')
worksheet = workbook.add_worksheet()
current_row = 0
try:
    with open('url_maps.json', 'r') as url_file:
        url_mappings = json.load(url_file)
    print 'Loaded url maps.'
except:
    print 'No url maps loaded'
    url_mappings = {}
for company_name, company_insights in results.iteritems():
    employees = company_insights['employees']
    if employees:
            for emp_name, em_deet in employees.iteritems():
                try:
                    worksheet.write(current_row, 0, company_name)
                    worksheet.write(current_row, 1,
                                    company_insights.get('website'))
                    worksheet.write(current_row, 2,
                                    company_insights.get('industry'))
                    worksheet.write(current_row, 3,
                                    company_insights.get('size'))
                    # Get short URL
                    try:
                        short_company = url_mappings[company_insights
                                                     .get('linkedin')]
                    except:
                        short_company = bt_conn.shorten(
                            company_insights.get('linkedin'))['url']
                    worksheet.write(current_row, 4,
                                    short_company)
                    worksheet.write(current_row, 5,
                                    emp_name)
                    worksheet.write(current_row, 6,
                                    em_deet.get('description'))
                    try:
                        short_person = url_mappings[em_deet.get('link')]
                    except:
                        short_person = bt_conn.shorten(
                            em_deet.get('link'))['url']
                    worksheet.write(current_row, 7,
                                    short_person)
                    # Save timestamp if exists
                    worksheet.write(current_row, 8,
                                    company_insights.get('processed'))
                    print 'Added: {person} ({company})'.format(
                          person=emp_name, company=company_name)
                    # Keep URL's to avoid re-checking
                    url_mappings[company_insights.get(
                        'linkedin')] = short_company
                    url_mappings[em_deet.get('link')] = short_person
                except:
                    pass
                current_row += 1
    current_row += 1  # Space out companies in the sheet
workbook.close()
with open('url_maps.json', 'w+') as url_file:
    json.dump(url_mappings, url_file)
print 'Saved url maps.'
