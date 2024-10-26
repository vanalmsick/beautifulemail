import os, re, datetime

import markdown2

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from smtplib import SMTP, SMTP_SSL

import numpy as np
import pandas as pd
from pandas.io.formats.style import Styler
from bs4 import BeautifulSoup
import sass


def _standarise_email(obj):
    """Converts """
    return obj

class DataFrameToHTML:
    def __init__(self, df, index=True, header=True, index_names=False):
        if isinstance(df, Styler):
            self.styled_df = df
        else:
            self.styled_df = df.style
        self.df = self.styled_df.data

        self.has_index = index
        self.has_header = header
        self.has_index_names = index_names

        self.col_num_fmt = {}
        self.col_style = {}


    def col_num_fmt_auto(self):
        """Automatically detectes the number format of a column and formatts it"""

        # get all date columns
        for col_name, col_series in self.df.select_dtypes(include=["datetime", "datetimetz"]).items():
            self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else num.strftime('%Y-%m-%d')

        # get all numeric columns
        for col_name, col_series in self.df.select_dtypes(include=["number"]).items():
            col_series_mod = col_series.replace(0, np.nan).abs()
            low = col_series_mod.quantile(0.2)
            high = col_series_mod.quantile(0.8)

            # check if percentages
            if -2 < low and high < 2:
                self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else '{:,.1f}%'.format(num / 100)
            # check if small number
            elif high < 1_000 and "int" not in str(col_series.dtype):
                self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else '{:,.0f}'.format(num)
            # check if iso cob date
            elif 1900_00_00 < low and high < 2100_00_00:
                self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else '{:.0f}'.format(num)
            # check if large number in millions
            elif low > 10_000_000:
                self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else '{:,.0f}'.format(num / 1_000_000)
            # else normal number format
            else:
                self.col_num_fmt[col_name] = lambda num: '' if pd.isna(num) else '{:,.0f}'.format(num)


    def col_num_fmt(self, column, num_format):
        """
        Set the number format of one or several columns.

        Args:
            column (str or list of str): column name e.g. 'RoE' or ['RoE', 'revenue']
            num_format (str): excel number format string e.g. '0.0%;[Red]-0.0%' or 'yyyy-mm-dd' or '#,##0'
        """
        if type(column) is str:
            column_lst = [column]
        for column in column_lst:
            self.col_num_fmt[column] = num_format

    def col_styles(self, column, classes=[], css_style={}):
        if type(column) is not list:
            column = [column]
        for col in column:
            self.col_style[col] = '{\n' + '\n'.join([f'@extend .{i};' for i in classes]) + '\n' + str(css_style)[1:]


    def to_html(self, index=None, header=None, index_names=None):
        if index is not None:
            self.has_index=index
        if header is not None:
            self.has_header=header
        if index_names is not None:
            self.has_index_names=index_names

        # apply number formatting
        for col, fmt in self.col_num_fmt.items():
            self.df[col] = self.df[col].apply(fmt)

        df_html = self.styled_df.to_html(index=self.has_index, header=self.has_header, index_names=self.has_index_names)

        style_html, table_html = df_html.split('</style>')
        style_html = re.sub(re.compile('<.*?>'), '', style_html)

        # add column styles
        for col, style in self.col_style.items():
            i = self.df.columns.to_list().index(col)
            style_html += f'#T_{self.styled_df.uuid} tbody .col{i} {style}\n'

        return style_html, table_html


    def __str__(self):
        style_html, table_html = self.to_html()
        return f'<style>\n{style_html}\n</style>\n{table_html}'



def send_email(
        conn,
        from_,
        to_=[],
        cc_=[],
        bcc_=[],
        subject='',
        body_text='',
        body_html='',
        body_markdown='',
        add_sender_cc=False,
        attachments=[],
        embedded_imgs=[],
        dry_run=False,
        template='msft_plain_blue'
        ):

    # ensure recipients are lists
    if type(to_) is str:
        to_ = [to_]
    if type(cc_) is str:
        cc_ = [cc_]
    if type(bcc_) is str:
        bcc_ = [bcc_]

    if add_sender_cc:
        cc_ += [from_]

    # read-in template
    if template is None:
        template_html = '{body_html}'
    else:
        # standard template included in package
        if "." not in template:
            this_file_path = os.path.dirname(os.path.abspath(__file__))
            template = os.path.join(this_file_path, "templates", f"{template}.html")

        with open(template, "r") as file:
            template_html = file.read()


    # build email
    msg = MIMEMultipart("related")
    msg['Subject'] = subject
    msg['From'] = msg_from = _standarise_email(from_)

    if len(to_) > 0:
        msg['To'] = ','.join([_standarise_email(i) for i in to_])
    if len(cc_) > 0:
        msg['CC'] = ','.join([_standarise_email(i) for i in cc_])
    msg_to = ','.join(list(set([_standarise_email(i) for i in to_ + cc_ + bcc_])))

    if body_text != '':
        msg.attach(MIMEText(body_text, 'plain'))
    if body_markdown != '':
        body_html = markdown2.markdown(body_markdown, extras=['breaks', 'tables', 'strike', 'code-friendly', 'fenced-code-blocks', 'footnotes', 'task_list'])
    if body_html != '':
        body_html = template_html.replace('{body_html}', body_html)

        # combine style sheets
        soup = BeautifulSoup(body_html, features="lxml")
        style_html = ''
        for i, style in enumerate(soup.findAll('style')):
            style_html += style.encode_contents().decode("utf-8")
            #if i > 0:
            style.decompose()
        head = soup.find('head')
        style = BeautifulSoup('<style>' + sass.compile(string=style_html) + '</style>', features="lxml")
        head.append(style)

        body_html = soup.prettify()

        msg.attach(MIMEText(body_html, 'html'))

    # embedd images
    for i, embed_i_path in enumerate(embedded_imgs):
        with open(embed_i_path, "rb") as file:
            embed_i = MIMEImage(file.read())
        embed_i['Content-ID'] = f'<image{i+1}>'
        msg.attach(embed_i)

    # add attchments
    for attach_i_path in attachments:
        attach_i_name = os.path.basename(attach_i_path)
        with open(attach_i_path, 'rb') as file:
            attach_i = MIMEApplication(file.read(), Name=attach_i_path)
        attach_i['Content-Disposition'] = f'attachment;filename="{attach_i_name}"'
        msg.attach(attach_i)

    # send email
    send_props = {
        'From': msg.get('From', None),
        'To': msg.get('To', None),
        'Cc': msg.get('CC', None),
        'Bcc': ','.join([_standarise_email(i) for i in bcc_]),
        'Subject': subject,
        'Body': body_html if body_html != '' else body_text,
        'Attachments': ',\n'.join(attachments),
        'Embedded': ',\n'.join(embedded_imgs)
        }
    try:
        if dry_run:
            send_props['Mode'] = 'DRYRUN'
            send_props['Status'] = 'SUCESS'
            send_props['Status Code'] = 0
        else: # real email
            send_props['Mode'] = 'REAL'
            conn.sendmail(msg_from, msg_to, msg.as_string())
            send_props['Status'] = 'SUCESS'
            send_props['Status Code'] = 1
    except Exception as e:
        send_props['Status'] = f'ERROR {e}'
    finally:
        send_props['Timestamp'] = datetime.datetime.now().isoformat()

        print(f"{send_props['Mode']} Email (Status: {send_props['Status']}) '{send_props['Subject']}' sent to: {msg_to}")
        return send_props






class Connection:
    """
    Class for connecting to smtp server.

    Example:
        ```python
        from beautifulemail import Connection, send_email

        with Connection('workbook.xlsx', mode='r', style='elegant_blue') as conn:
            ws1 = conn.to_excel(df1, sheetname='My Sheet', mode='a', startrow=0, startcol=0)
            ws2 = conn.to_excel(df2, sheetname='My Sheet', mode='a', startrow=20, startcol=0)
        ```
    """

    def __init__(
        self,
        host='',
        port=0,
        local_hostname=None,
        ssl=False,
        user=None,
        password=None,
        **kwargs,
    ):
        if ssl:
            self.conn = SMTP_SSL(host=host, port=port, local_hostname=local_hostname, **kwargs)
        else:
            self.conn = SMTP(host=host, port=port, local_hostname=local_hostname, **kwargs)

        if user is not None:
            self.conn.login(user=user, password=password)

        self.sent_emails = []


    def __enter__(self):
        if not hasattr(self, "conn"):
            raise Exception(
                "Wrong usage! Please run it this way:\n>>> from beautifulemail import Connection\n>>> with Connection('workbook.xlsx', mode='r', theme='elegant_blue') as conn:\n>>>     ws1 = writer.write_df(df1, sheetname='My Sheet'"
            )
        return self


    def __exit__(self, type, value, traceback):
        # ToDo: add exception handling here
        self.conn.close()
        self = None

    def send_email(self, *args, **kwargs):
        results = send_email(conn=self.conn, *args, **kwargs)
        self.sent_emails.append(results)
        return results

    def save_sent_email_summary(self, file_path):
        df = pd.DataFrame(self.sent_emails)
        if '.csv' in file_path:
            df.to_csv(file_path)
        elif '.xls' in file_path:
            df.to_excel(file_path)
        else:  # folder path
            file_path = os.path.join(file_path, 'sent_emails.xlsx')
            df.to_excel(file_path)




# Test Email
if __name__ == '__main__':

    EMAIL_HOST = os.environ.get('EMAIL_HOST')  # smtp.gmail.com
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))  # 465
    EMAIL_USER = os.environ.get('EMAIL_USERNAME')  # my_email@gmail.com
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # my_secret_password

    example_df = pd.DataFrame(
        {
            "client": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "industry": [
                "ASEET MANAGEMENT",
                "ASEET MANAGEMENT",
                "BANK",
                "INSURANCE",
                "VERY VERY VERY VERY VERY LONG INSUSTRY NAME",
                "BANK",
                "COMMODITY BROKER",
                "INSURANCE",
                ],
            "employees": [25_000, 17_000_000, 14, 9_000, 12_000_000, 9_000, np.nan, 4_000_000],
            "inception": [
                datetime.datetime(2022, 1, 1),
                datetime.datetime(2000, 10, 30),
                datetime.datetime(2010, 5, 6),
                np.nan,
                datetime.datetime(1997, 1, 1),
                datetime.datetime(1962, 1, 1),
                datetime.datetime(2003, 11, 10),
                datetime.datetime(2022, 1, 1),
                ],
            "last_contact": [
                datetime.datetime(2022, 1, 1, 10, 2, 5),
                datetime.datetime(2000, 10, 30),
                datetime.datetime(2010, 5, 6),
                np.nan,
                datetime.datetime(1997, 1, 1),
                datetime.datetime(1962, 1, 1),
                datetime.datetime(2003, 11, 10, 10, 2, 5),
                datetime.datetime(2022, 1, 1),
                ],
            "RoE": [0.05, -0.05, 0.15, 1.05, -0.02, np.nan, 0.08, 0.05],
            "revenue": [
                50_000_000.4387,
                np.nan,
                63_000_000.4387,
                25_000.4387,
                25_000_000.4387,
                -50_000_000.4387,
                76_000_000.4387,
                25_000.4387,
                ],
            }
        )
    example_df.set_index("client", inplace=True)


    #example_df_html = DataFrameToHTML(df=example_df)
    #example_df_html.num_fmt_auto()

    styled = example_df.style.applymap(lambda i: '', subset=pd.IndexSlice[:, ['last_contact', 'revenue']])
    styled_example_df_html = DataFrameToHTML(df=styled)
    styled_example_df_html.col_num_fmt_auto()
    styled_example_df_html.col_styles(column=['last_contact', 'revenue'], classes=['bg_light_blue'], css_style={})


    email_to = os.environ.get('EMAIL_TO', EMAIL_USER)  # my_email@gmail.com
    email_from = os.environ.get('EMAIL_FROM', EMAIL_USER)  # my_email@gmail.com
    email_subject = 'My Test'

    email_body_markdown = """
Hi,

This is a test email with **bold text**, *italic text*, ~~strikethrough text~~, <mark>highlited text</mark>, [hyperlink text](https://www.google.com), and text that could be footnoted<note>[1]</note>.

""" + str(styled_example_df_html) + """

# This would be a Heading 1 of an ordered list

1. First step
2. Second step
3. Third step

## This would be a Heading 2 of an unordered list

- bullet point one
- bullet point two
- bullet point three

### This would be a Heading 3 of a table

| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |

#### This would be a Heading 4 of a text blocks

Code block:
```python
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

Text block/quote:
> This has to be a very
>  
> very important person's quote


<footnote><note>[1]</note> Very important footnote</footnote>
    """

    with Connection(host=EMAIL_HOST, port=EMAIL_PORT, ssl=True, user=EMAIL_USER, password=EMAIL_PASSWORD) as conn:
        status = conn.send_email(
            from_=email_from,
            to_=email_to,
            subject=email_subject,
            body_markdown=email_body_markdown,
            attachments=['../README.md'],
            dry_run=False
            )

        with open('email.html', 'w') as file:
            file.write(status['Body'])
        conn.save_sent_email_summary('.')