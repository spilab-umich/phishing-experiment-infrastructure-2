# Customizing the Inbox


This page provides guidance for working with different project features, including:

- Customizing warning template
- Customizing phishing links
- Customizing warning behavior
- Phishing hyperlink redirection

## Customizing the base warning template
Our warnings build off of a template base located in `email_client/mail/templates/mail/warnings/1.html`. You can adjust this warning template file to change the appearance of the anti-phishing warning.

## Customizing phishing links
The phishing link for each user/phishing email combination is saved as a Django database object in `config/init_db.py`. You can input your own phishing links by adjusting the value of `list_of_p_domains` in this file.

## Customizing warning behavior

Our warnings have two different features:
1. time delay: phishing links are unclickable for a certain amount of time (e.g., 3 seconds)
2. focused attention: users must click on the URL displayed inside the warning to proceed to the website

Warning behavior is handled in three places: `email_client/mail/views.py`, `email_client/mail/templates/mail/email.html` and `email_client/mail/static/js/warnings.js`. 

`email_client/mail/views.py` sets four variables:
1. a warning's time delay value (0 - 5 seconds)
2. whether a warning has focused attention (True/False)
3. a warning's subheader text (unique for different types of warnings)
4. the legitimate link associated with a phishing link (see Customizing Hyperlink Redirection)

These variables are passed to `email_client/mail/templates/mail/email.html`. At the bottom of this file is a `<script>` tag that identifies whether an email should display a warning (i.e., is an email a phish or a false positive). If the email should display a warning, this script passes the warning's paramters to the function `load_warning` from `email_client/mail/static/js/warnings.js`, which then implements the warning.

## Customizing recording behavior

`email_client/mail/static/js/warnings.js` also contains the code for recording user clicks and hovers over email hyperlinks. These behaviors can be customized to fit your use cases.

## Phishing hyperlink redirection
To prevent users from clicking on actual phishing links, our inbox uses a clickjacking technique in `warnings.js` and `mail/templates/mail/email.html`. This lets the inbox display a realistic phishing URL without having to register a phishy domain (and possibly triggering an organization's cybersecurity incident response team).

Simply put:

- Phishing links are made unclickable by default when the EML files are imported in `config/init_db.py`. This is accomplished by modifying the phishing link's (selcted by the emails `phish_id` key in `config/emails.json`) `onclick` property to `return false;`
- When a user navigates to an email, `views.py` determines if this email is a phish. If it is, the legitimate/safe URL is included in the payload sent to the user's browser.
- The legitimate/safe link associated with a phishing link (e.g., <u>walmart.com</u> for the phishing link <u>walmart-payment.com</u>) is read by the `email.html` template.
- If an email is a phish, `email.html` calls `warnings.js` which assigns a new `onclick` function to the disabled phishing links. When clicked, the disabled phishing link opens a new browser window containing the legitimate URL.

This functionality should be removed if you do not intend to use phishing links. 


```python

```
