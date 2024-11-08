# Email Inbox with Custom Phishing Warnings

This is the source code for the IEEE Security & Privacy paper: 

*Justin Petelka, Benjamin Berens, Carlo Sugatan, Melanie Volkamer, and Florian Schaub. "Restricting the Link: Effects of Focused Attention and Time Delay on Phishing Warning Effectiveness." Under Review; IEEE Symposium on Security and Privacy. 2025.*

This repo creates a website that displays emails, records user hovers and clicks, and displays custom anti-phishing warnings. We used this project to identify differences in how people click and hover in emails when confronted with different types of anti-phishing warning.

This source code requires `Python 3.10` and the Python library `Django 4.1` (https://docs.djangoproject.com/en/4.1/).

## Features
This project displays selected emails inside of a realistic email inbox, records user mouse interactions with hyperlinks (e.g., clicks and hovers), and displays customized anti-phishing warnings.

Our inbox also can display phishing URLs. We use a [clickjacking method](docs/inbox_customization.md#phishing-hyperlink-redirection) so participants who click on phishing URLs are re-directed to legitimate websites. We accomplish this by replacing the default `onclick` method for the phishing link.

## Installation
Please see our [Installation document](docs/installation_readme.md) to for instructions and requirements to deploy this project on your device.

## Customization
Please see our [Customization document](docs/inbox_customization.md) to learn how to change the default inbox behavior (e.g., warnings, phishing links, link redirection).

## Repo Maintenance
We appreciate your contributions to this project, but this repo is not regularly maintained. We will address pull requests as we are able to, but might not be able to offer help with installation and debugging beyond these documents.


```python

```
