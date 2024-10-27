# -*- coding: utf-8 -*-
import os, datetime
import unittest.mock
import numpy as np
import pandas as pd
from beautifulemail.base import Connection, DataFrameToHTML


def test_full_implementation():
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

    styled = example_df.style.applymap(lambda i: '', subset=pd.IndexSlice[:, ['last_contact', 'revenue']])
    styled_example_df_html = DataFrameToHTML(df=styled)
    styled_example_df_html.col_num_fmt_auto()
    styled_example_df_html.col_styles(column=['last_contact', 'revenue'], classes=['bg_light_blue'], css_style={})

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

    with unittest.mock.patch('smtplib.SMTP', autospec=True) as mock:
        with Connection() as conn:
            conn.conn = mock
            status = conn.send_email(
                from_='test@test.com',
                to_='test@test.com',
                subject='My Email subject',
                body_markdown=email_body_markdown,
                dry_run=False
                )

            with open('email.html', 'w') as file:
                file.write(status['Body'])
            conn.save_sent_email_summary('.')

    assert True