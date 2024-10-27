# BeautifulEmail

> **⚠️🏗️️ Note:**
> This is only the first version - actively working on additional features!

BeautifulEmail is a python package that makes it easy and quick to send beautifully formatted emails with beuatiful tables/dataframes. BeautifulEmail is for Data Scientists with a deadline.
  
> **Email Example:**
> 
> <img src="https://github.com/vanalmsick/beautifulemail/raw/main/docs/docs/imgs/email_preview.jpg" alt="Email Preview" style="width:40%;border: 1px solid #D9D9D9;"/>

## Getting it

```console
$ pip install beautifulemail
```
**Update Package:** *(execute <ins>regularly</ins> to get the latest features)*
```console
$ pip install beautifulemail --upgrade
```
  
<br>
  
## How to use:

```python
from beautifulemail import Connection, DataFrameToHTML

df_styled = ...

df_html = DataFrameToHTML(df=df_styled)

# format numbers automatically 
df_html.col_num_fmt_auto()

# add background styling to columns
df_html.col_styles(column=['last_contact', 'revenue'], classes=['bg_light_blue'])
df_html.col_styles(column=['last_contact'], classes=['text_color_amber'])

# use markdown to write email - more infoss here: www.markdownguide.org/cheat-sheet/
email_body_markdown = f"""
Hi,

This is a test email with **bold text**, *italic text*, ~~strikethrough text~~, <mark>highlited text</mark>, [hyperlink text](https://www.google.com), and text that could be footnoted<note>[1]</note>.

# This would be a Heading 1 of an ordered list

1. First step
2. Second step
3. Third step

{df_html}

Embedded image:
<img src="cid:image1" style="width: 100px;">

Best wishes,
Me
    """

    # connect to email server
    with Connection(host='smtp.gmail.com', port=465, ssl=True, user='myemai@gmail.com', password='my_password') as conn:
        # send email
        status = conn.send_email(
            from_='my_emai@gmail.com',
            to_=['your_emai@gmail.com', 'second_emai@gmail.com'],
            subject='Email Subject',
            body_markdown=email_body_markdown,
            attachments=['./README.md'],
            embedded_imgs=['./email_preview.jpg'],
            dry_run=False
            )
        
        # status contains all the email information including the html body
        print('Email sent:', status)

        # save sent email documntation/summary as excel
        conn.save_sent_email_summary('sent_emails.xlsx')
```

<br><br>