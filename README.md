# BeautifulEmail

> **⚠️🏗️️ Note:**
> This is only the first version - actively working on additional features!

BeautifulEmail is a python package that makes it easy and quick to send beautifully formatted emails with beuatiful tables/dataframes. BeautifulEmail is for Data Scientists with a deadline.
  
<img src="https://github.com/vanalmsick/beautifulexcel/raw/main/docs/docs/imgs/email_preview.png" alt="Email Preview" style="max-height:600px;border: 1px solid #555;"/>

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

df_html = DataFrameToHTML(df=styled)
df_html.col_num_fmt_auto()
df_html.col_styles(column=['last_contact', 'revenue'], classes=['bg_light_blue'])
df_html.col_styles(column=['last_contact'], classes=['text_color_amber'])

email_body_markdown = f"""
Hi,

This is a test email with **bold text**, *italic text*, ~~strikethrough text~~, <mark>highlited text</mark>, [hyperlink text](https://www.google.com), and text that could be footnoted<note>[1]</note>.

# This would be a Heading 1 of an ordered list

1. First step
2. Second step
3. Third step

{df_html}

Best wishes,
Me
    """

    with Connection(host='smtp.gmail.com', port=465, ssl=True, user='myemai@gmail.com', password='my_password') as conn:
        status = conn.send_email(
            from_='myemai@gmail.com',
            to_='youremai@gmail.com',
            subject='Email Subject',
            body_markdown=email_body_markdown,
            attachments=['../README.md'],
            dry_run=False
            )
```

<br><br>