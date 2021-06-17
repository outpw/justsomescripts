import pandas as pd
import os

os.chdir('C:/Users/phwh9568/CUPubs_mailprep') #set the directory to your folder with the pub data

year = '(2020)'

df = pd.read_csv('CUPublications_2017FRPA.csv', encoding = 'iso-8859-1', low_memory = False)
df.fillna('', inplace=True)

col_list = ['Name', 'Authors', 'Email', 'Primary group', 'Title OR Chapter Title', 'Canonical journal title', 'Volume', 'Issue', 'DOI', 'Primary group', 'Email']
df = df[df.columns.intersection(col_list)]

# function that finds publication metadata and concatenates them into a citation
def cite(irow):
    if irow['Authors'] == '':
        auths = ''
    else:
        auths = irow['Authors']+'.'

    date = ' '+year+'.'

    if irow['Title OR Chapter Title'] == '':
        title = ''
    else:
        title = ' '+irow['Title OR Chapter Title']+'.'

    if irow['Canonical journal title'] == '':
        pub = ''
    else:
        pub = ' '+irow['Canonical journal title']+'.'

    if irow['Volume'] == '':
        vol = ''
    else:
        vol = ' '+irow['Volume']+'.'

    if irow['Issue'] == '':
        iss = ''
    else:
        iss = ' '+irow['Issue']+'.'

    if irow['DOI'] == '':
        doi = ''
    else:
        doi = ' '+irow['DOI']+'.'

    citation = auths + date + title + pub + vol + iss + doi

    return citation

# function that splits full names into individual first, middle, last name fields
def names(irow):

    if len(irow) == 0:
        nl = ''
        nf = ''
        nm = ''

    else:
        n = irow['Name'].title()

        nl = n.split(', ')[0]

        if len(n.split(', ')) > 1:

            nfm = n.split(', ')[1]

            if len(nfm.split(' ')) > 1:
                nf = nfm.split(' ')[0]
                nm = nfm.split(' ')[1]
            else:
                nf = nfm
                nm = ''
        else:
            nf =''
            nm =''

    return nl,nf,nm

# Apply the functions across rows in the dataframe
df['Pub'] = df.apply(lambda row: cite(row), axis = 1)
df['Last Name'] = df.apply(lambda row: names(row)[0], axis = 1)
df['First Name'] = df.apply(lambda row: names(row)[1], axis = 1)
df['Middle Name'] = df.apply(lambda row: names(row)[2], axis = 1)

#Now create new dataframe of just authors and citations
col_list2 = ['Name', 'Pub']
df2 = df[col_list2].copy() #create the new daframe named df2


df2 = df2.assign(group = df.groupby('Name').cumcount()) #creating the groups and adding a new 'group' column
citations = df2.pivot(index = 'Name', columns = 'group') #pivot function with names in the index position (vertical) and groups become columns (horizontal)

#pivot creates multi-index dataframe. This will reset it to a single index (or in other words takes the 2 header row and makes 1 header row)
citations.columns =  [col[0] + '_' + str(col[1]+1) for col in citations.columns.values]


col_list3 = ['Name', 'Last Name', 'First Name', 'Middle Name', 'Primary group', 'Email'] #the columns we need for our new dataframe
df3 = df[col_list3] #create new df3 that consists of just names, departments, and emails from original df

contacts = df3.drop_duplicates(subset = ['Name'], keep = 'first')
contacts.reset_index(inplace=True)
contacts = contacts.drop(columns=['index'])

#merge the citations back to the names & contact info
finaldf = contacts.merge(citations, how= 'left', left_on = 'Name', right_on = 'Name')
finaldf.to_csv('test2.csv') #view the results
